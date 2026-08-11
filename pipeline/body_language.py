#!/usr/bin/env python3
"""Extract body-language metrics from video via MediaPipe Tasks (pose + face).

Samples frames at ~3 fps with OpenCV, runs PoseLandmarker and FaceLandmarker
(with iris landmarks + blendshapes), writes body_metrics.json per
pipeline/SPECS.md. Skips cleanly ({"has_video": false}) for audio-only input.

Note: built on the mediapipe >= 1.0 Tasks API (the legacy `solutions` API was
removed). Model files live in pipeline/models/ — fetched by setup.sh.
Blendshapes give a Duchenne proxy: mouthSmile + cheekSquint (AU12 + ~AU6).
"""
import argparse
import json
import sys
from pathlib import Path

SAMPLE_FPS = 3.0
SMILE_THRESHOLD = 0.30       # mean(mouthSmileL/R) blendshape score
DUCHENNE_SQUINT = 0.20       # cheek/eye squint co-activation for Duchenne
# Pose landmark indices (33-point model)
NOSE, L_EAR, R_EAR = 0, 7, 8
L_SHOULDER, R_SHOULDER, L_HIP, R_HIP = 11, 12, 23, 24
L_WRIST, R_WRIST = 15, 16
# Face mesh indices
L_EYE_OUT, L_EYE_IN, R_EYE_IN, R_EYE_OUT = 33, 133, 362, 263
L_EYE_TOP, L_EYE_BOT, R_EYE_TOP, R_EYE_BOT = 159, 145, 386, 374
R_IRIS, L_IRIS = 468, 473    # iris centers


def mid(a, b):
    return ((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)


def uprightness_from_pose(lm):
    """0–1: shoulder-line level + torso vertical + head over shoulders."""
    import math

    sh_l, sh_r = lm[L_SHOULDER], lm[R_SHOULDER]
    hip_l, hip_r = lm[L_HIP], lm[R_HIP]
    ear_l, ear_r = lm[L_EAR], lm[R_EAR]
    sh_mid, hip_mid, ear_mid = mid(sh_l, sh_r), mid(hip_l, hip_r), mid(ear_l, ear_r)
    sh_w = max(abs(sh_l.x - sh_r.x), 1e-6)

    # Shoulder line tilt vs. horizontal (0 = level)
    tilt = abs(math.atan2(sh_l.y - sh_r.y, sh_l.x - sh_r.x))
    tilt = min(tilt, math.pi - tilt)  # symmetric
    tilt_score = max(0.0, 1.0 - tilt / 0.35)

    # Torso lean: shoulder-mid over hip-mid, horizontal offset vs. shoulder width
    lean = abs(sh_mid[0] - hip_mid[0]) / sh_w
    lean_score = max(0.0, 1.0 - lean / 0.5)

    # Head position: ear-mid horizontal offset over shoulder-mid (slouch/jut)
    head_off = abs(ear_mid[0] - sh_mid[0]) / sh_w
    head_score = max(0.0, 1.0 - head_off / 0.5)

    return 0.4 * tilt_score + 0.3 * lean_score + 0.3 * head_score


def gaze_class(face_lm):
    """Classify gaze per frame: toward_camera / left / right / down."""
    def ratio(iris, inner, outer, top, bot):
        h_span = outer.x - inner.x
        v_span = bot.y - top.y
        h = (iris.x - inner.x) / h_span if abs(h_span) > 1e-6 else 0.5
        v = (iris.y - top.y) / v_span if abs(v_span) > 1e-6 else 0.5
        return h, v

    rh, rv = ratio(face_lm[R_IRIS], face_lm[L_EYE_IN], face_lm[L_EYE_OUT],
                   face_lm[L_EYE_TOP], face_lm[L_EYE_BOT])
    lh, lv = ratio(face_lm[L_IRIS], face_lm[R_EYE_IN], face_lm[R_EYE_OUT],
                   face_lm[R_EYE_TOP], face_lm[R_EYE_BOT])
    h, v = (rh + lh) / 2.0, (rv + lv) / 2.0
    if v > 0.72:
        return "down"
    if h < 0.36:
        return "left"
    if h > 0.64:
        return "right"
    return "toward_camera"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="path to the original media file")
    ap.add_argument("--outdir", required=True, help="analysis output directory")
    args = ap.parse_args()

    inpath, outdir = Path(args.input), Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    outfile = outdir / "body_metrics.json"
    if not inpath.exists():
        print(f"ERROR: input not found: {inpath}", file=sys.stderr)
        return 1

    # Audio-only input → clean skip (trust media_info.json when present).
    info_path = outdir / "media_info.json"
    if info_path.exists():
        if not json.loads(info_path.read_text()).get("has_video"):
            outfile.write_text(json.dumps({"has_video": False}, indent=2))
            print("no video stream — wrote skip stub body_metrics.json")
            return 0

    try:
        import cv2
        import numpy as np
        import mediapipe as mp
        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision
    except ImportError as e:
        print(f"ERROR: missing dependency ({e}) — run setup.sh first.", file=sys.stderr)
        return 1

    models_dir = Path(__file__).parent / "models"
    pose_model = models_dir / "pose_landmarker_lite.task"
    face_model = models_dir / "face_landmarker.task"
    if not pose_model.exists() or not face_model.exists():
        print(f"ERROR: task models missing in {models_dir} — run setup.sh first.", file=sys.stderr)
        return 1

    cap = cv2.VideoCapture(str(inpath))
    if not cap.isOpened():
        outfile.write_text(json.dumps({"has_video": False}, indent=2))
        print("OpenCV could not open a video stream — wrote skip stub")
        return 0
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(src_fps / SAMPLE_FPS))

    mode = vision.RunningMode.VIDEO
    pose = vision.PoseLandmarker.create_from_options(
        vision.PoseLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=str(pose_model)),
            running_mode=mode,
        )
    )
    face = vision.FaceLandmarker.create_from_options(
        vision.FaceLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=str(face_model)),
            running_mode=mode,
            output_face_blendshapes=True,
        )
    )

    upright_ts, smile_ts, gaze_classes = [], [], []
    duchenne_frames, smile_frames = 0, 0
    nose_track, shoulder_x_track, wrist_active = [], [], []
    frames_analyzed = 0
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % step:
            frame_idx += 1
            continue
        t = frame_idx / src_fps
        ts_ms = int(t * 1000)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        pres = pose.detect_for_video(image, ts_ms)
        fres = face.detect_for_video(image, ts_ms)
        frames_analyzed += 1

        if pres.pose_landmarks:
            lm = pres.pose_landmarks[0]
            upright_ts.append({"t": round(t, 2), "v": round(uprightness_from_pose(lm), 2)})
            nose_track.append((t, lm[NOSE].x, lm[NOSE].y))
            shoulder_x_track.append(mid(lm[L_SHOULDER], lm[R_SHOULDER])[0])
            sh_y = mid(lm[L_SHOULDER], lm[R_SHOULDER])[1]
            wrists_up = any(
                lm[w].visibility > 0.5 and lm[w].y < sh_y + 0.25 for w in (L_WRIST, R_WRIST)
            )
            wrist_active.append((t, wrists_up, lm[L_WRIST].x, lm[L_WRIST].y,
                                 lm[R_WRIST].x, lm[R_WRIST].y))

        if fres.face_landmarks:
            flm = fres.face_landmarks[0]
            gaze_classes.append(gaze_class(flm))
            smile_v = 0.0
            squint_v = 0.0
            if fres.face_blendshapes:
                bs = {b.category_name: b.score for b in fres.face_blendshapes[0]}
                smile_v = (bs.get("mouthSmileLeft", 0) + bs.get("mouthSmileRight", 0)) / 2
                squint_v = max(
                    (bs.get("cheekSquintLeft", 0) + bs.get("cheekSquintRight", 0)) / 2,
                    (bs.get("eyeSquintLeft", 0) + bs.get("eyeSquintRight", 0)) / 2,
                )
            smile_ts.append({"t": round(t, 2), "v": round(smile_v, 2)})
            if smile_v >= SMILE_THRESHOLD:
                smile_frames += 1
                if squint_v >= DUCHENNE_SQUINT:
                    duchenne_frames += 1
        frame_idx += 1

    cap.release()
    pose.close()
    face.close()

    if frames_analyzed == 0:
        outfile.write_text(json.dumps({"has_video": False}, indent=2))
        print("no decodable frames — wrote skip stub")
        return 0

    # Posture aggregate
    uvals = np.array([p["v"] for p in upright_ts]) if upright_ts else np.array([])
    posture = {
        "shoulder_forward_score_ts": upright_ts,
        "uprightness_mean": round(float(uvals.mean()), 2) if uvals.size else None,
        "uprightness_trend": None,
        "start_vs_end_delta": None,
    }
    if uvals.size >= 6:
        slope = float(np.polyfit(np.arange(uvals.size), uvals, 1)[0]) * uvals.size
        posture["uprightness_trend"] = (
            "declining" if slope < -0.05 else "improving" if slope > 0.05 else "stable"
        )
        k = max(1, uvals.size // 10)
        posture["start_vs_end_delta"] = round(float(uvals[-k:].mean() - uvals[:k].mean()), 2)

    # Face aggregate
    face_block = {
        "smile_pct": round(100.0 * smile_frames / len(smile_ts), 1) if smile_ts else None,
        "smile_ts": smile_ts,
        "duchenne_available": True,
        "duchenne_pct_of_smiles": round(100.0 * duchenne_frames / smile_frames, 1)
        if smile_frames
        else None,
    }

    # Gaze aggregate
    n_gaze = len(gaze_classes)
    changes = sum(1 for a, b in zip(gaze_classes, gaze_classes[1:]) if a != b)
    gaze_block = {
        "toward_camera_pct": round(100.0 * gaze_classes.count("toward_camera") / n_gaze, 1)
        if n_gaze else None,
        "down_pct": round(100.0 * gaze_classes.count("down") / n_gaze, 1) if n_gaze else None,
        "stability_score_0to100": round(100.0 * (1.0 - changes / max(1, n_gaze - 1)))
        if n_gaze > 1 else None,
        "note": "toward_camera_pct only meaningful for youtube/on-camera context",
    }

    # Movement aggregate
    head_v = 0.0
    if len(nose_track) > 1:
        dists = [
            ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / max(t2 - t1, 1e-6)
            for (t1, x1, y1), (t2, x2, y2) in zip(nose_track, nose_track[1:])
        ]
        head_v = float(np.mean(dists))
    sway = 0.0
    if len(shoulder_x_track) > 1:
        sway = min(100.0, float(np.std(shoulder_x_track)) * 2000.0)
    gesture_pct = None
    if len(wrist_active) > 1:
        active = 0
        for (t1, up1, lx1, ly1, rx1, ry1), (t2, up2, lx2, ly2, rx2, ry2) in zip(
            wrist_active, wrist_active[1:]
        ):
            moving = (
                ((lx2 - lx1) ** 2 + (ly2 - ly1) ** 2) ** 0.5
                + ((rx2 - rx1) ** 2 + (ry2 - ry1) ** 2) ** 0.5
            ) / max(t2 - t1, 1e-6) > 0.15
            if up2 and moving:
                active += 1
        gesture_pct = round(100.0 * active / (len(wrist_active) - 1), 1)

    metrics = {
        "has_video": True,
        "frames_analyzed": frames_analyzed,
        "posture": posture,
        "face": face_block,
        "gaze": gaze_block,
        "movement": {
            "head_velocity_mean": round(head_v, 3),
            "sway_score_0to100": round(sway),
            "gesture_active_pct": gesture_pct,
        },
    }
    outfile.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(
        f"body metrics -> {outfile} ({frames_analyzed} frames, "
        f"uprightness {posture['uprightness_mean']}, smile {face_block['smile_pct']}%, "
        f"gaze-to-camera {gaze_block['toward_camera_pct']}%)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

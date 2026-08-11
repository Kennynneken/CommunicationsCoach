#!/usr/bin/env python3
"""Merge vocal + body metrics onto a shared 1-second timeline.

Reads transcript.json, vocal_metrics.json, body_metrics.json (and audio.wav
for per-second pitch/intensity) from --outdir; writes timeline.json with
per-second bins plus cross-channel incongruence flags per pipeline/SPECS.md.
"""
import argparse
import json
import sys
from pathlib import Path


def ts_str(t):
    m, s = divmod(int(t), 60)
    return f"{m:02d}:{s:02d}"


def nearest_series_value(series, t, tolerance=1.0):
    """series: [{"t":..,"v":..}] -> value nearest to t within tolerance."""
    best, best_d = None, tolerance
    for p in series:
        d = abs(p["t"] - t)
        if d <= best_d:
            best, best_d = p["v"], d
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", required=True, help="analysis dir with the metric JSONs")
    args = ap.parse_args()
    outdir = Path(args.outdir)

    needed = ["transcript.json", "vocal_metrics.json", "body_metrics.json"]
    missing = [n for n in needed if not (outdir / n).exists()]
    if missing:
        print(f"ERROR: missing {missing} in {outdir} — run earlier pipeline stages first.",
              file=sys.stderr)
        return 1

    try:
        import numpy as np
        import parselmouth
    except ImportError as e:
        print(f"ERROR: missing dependency ({e}) — run setup.sh first.", file=sys.stderr)
        return 1

    transcript = json.loads((outdir / "transcript.json").read_text(encoding="utf-8"))
    body = json.loads((outdir / "body_metrics.json").read_text(encoding="utf-8"))
    duration = transcript.get("duration_s") or 0
    words = transcript.get("words", [])
    has_video = body.get("has_video", False)

    # Per-second pitch/intensity from audio
    pitch_arr = intens_arr = None
    audio = outdir / "audio.wav"
    if audio.exists():
        snd = parselmouth.Sound(str(audio))
        pitch = snd.to_pitch_ac(pitch_floor=60, pitch_ceiling=400)
        intensity = snd.to_intensity()
        p_times = pitch.xs()
        p_vals = pitch.selected_array["frequency"]
        i_times = intensity.xs()
        i_vals = intensity.values[0]
        pitch_arr = (np.array(p_times), np.array(p_vals))
        intens_arr = (np.array(i_times), np.array(i_vals))

    n_secs = int(duration) + (1 if duration % 1 > 0.05 else 0)
    smile_series = (body.get("face") or {}).get("smile_ts", []) if has_video else []
    upright_series = (body.get("posture") or {}).get("shoulder_forward_score_ts", []) if has_video else []

    timeline = []
    for s in range(max(n_secs, 1)):
        lo, hi = float(s), float(s + 1)
        in_bin = [w for w in words if lo <= w["start"] < hi]
        speaking = bool(in_bin) or any(w["start"] < lo < w["end"] for w in words)
        wpm_local = len(in_bin) * 60

        pitch_sd_local = None
        if pitch_arr is not None:
            t_arr, v_arr = pitch_arr
            mask = (t_arr >= lo) & (t_arr < hi) & (v_arr > 0)
            if mask.sum() >= 3:
                pitch_sd_local = round(float(np.std(v_arr[mask])), 1)
        intensity_local = None
        if intens_arr is not None:
            t_arr, v_arr = intens_arr
            mask = (t_arr >= lo) & (t_arr < hi) & np.isfinite(v_arr) & (v_arr > 0)
            if mask.any():
                intensity_local = round(float(np.mean(v_arr[mask])), 1)

        entry = {
            "t": s,
            "speaking": speaking,
            "wpm_local": wpm_local,
            "pitch_sd_local": pitch_sd_local,
            "intensity": intensity_local,
        }
        if has_video:
            mid_t = lo + 0.5
            smile_v = nearest_series_value(smile_series, mid_t)
            entry["uprightness"] = nearest_series_value(upright_series, mid_t)
            entry["smiling"] = (smile_v is not None and smile_v >= 0.30)
            entry["gaze_class"] = None  # per-frame classes are aggregated in body_metrics
            entry["gesture_active"] = None
        timeline.append(entry)

    # ---- Incongruence flags ----
    flags = []

    def quartile(vals, q):
        vals = sorted(v for v in vals if v is not None)
        if not vals:
            return None
        return vals[min(len(vals) - 1, int(q * len(vals)))]

    # flat_face_while_storytelling: continuous speech >= 10s where smile and
    # pitch variance are both in the bottom quartile.
    if has_video and timeline:
        sd_q1 = quartile([e["pitch_sd_local"] for e in timeline if e["speaking"]], 0.25)
        run = []
        for e in timeline + [{"speaking": False, "t": len(timeline)}]:
            if e["speaking"]:
                run.append(e)
                continue
            if len(run) >= 10:
                low_pitch = [x for x in run if x["pitch_sd_local"] is not None
                             and sd_q1 is not None and x["pitch_sd_local"] <= sd_q1]
                smiles = [x for x in run if x.get("smiling")]
                if len(low_pitch) >= len(run) * 0.4 and len(smiles) <= len(run) * 0.1:
                    flags.append({
                        "flag": "flat_face_while_storytelling",
                        "start": run[0]["t"], "end": run[-1]["t"],
                        "desc": f"{ts_str(run[0]['t'])}–{ts_str(run[-1]['t'])}: "
                                "continuous speech with monotone pitch and no smile — "
                                "the audience hears a story but sees/feels nothing.",
                    })
            run = []

    # energy_body_mismatch: loud but static body.
    if has_video:
        gesture_pct = (body.get("movement") or {}).get("gesture_active_pct")
        sway = (body.get("movement") or {}).get("sway_score_0to100")
        i_vals_tl = [e["intensity"] for e in timeline if e["intensity"] is not None]
        if i_vals_tl and gesture_pct is not None and gesture_pct < 15 and (sway or 0) < 15:
            i_q3 = quartile(i_vals_tl, 0.75)
            loud_secs = [e["t"] for e in timeline
                         if e["intensity"] is not None and e["intensity"] >= i_q3]
            if loud_secs:
                flags.append({
                    "flag": "energy_body_mismatch",
                    "timestamps": loud_secs[:20],
                    "desc": "Vocal intensity peaks while the body stays static "
                            f"(gestures {gesture_pct}%, sway {sway}) — talking big, "
                            "standing dead. Peaks at: "
                            + ", ".join(ts_str(t) for t in loud_secs[:8]),
                })

    # posture_collapse: uprightness drops > 0.15 from session start.
    if has_video:
        delta = (body.get("posture") or {}).get("start_vs_end_delta")
        if delta is not None and delta < -0.15:
            flags.append({
                "flag": "posture_collapse",
                "desc": f"Uprightness fell {abs(delta):.2f} from session start — "
                        "posture collapsed as the session went on.",
            })

    out = {
        "duration_s": duration,
        "has_video": has_video,
        "timeline": timeline,
        "incongruence_flags": flags,
    }
    (outdir / "timeline.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"timeline -> {outdir}/timeline.json ({len(timeline)} bins, {len(flags)} incongruence flags)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

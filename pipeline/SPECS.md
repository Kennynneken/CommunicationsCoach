# Pipeline module specifications

All scripts take `--input` and `--outdir` arguments unless noted. All JSON is
UTF-8, pretty-printed. Times are seconds from media start, floats, 2 decimals.

---

## extract_audio.sh
`extract_audio.sh <media_file> <outdir>`
- ffmpeg → `<outdir>/audio.wav`, 16 kHz, mono, pcm_s16le.
- Also emit `<outdir>/media_info.json`: duration, has_video (bool), resolution,
  fps (via ffprobe).

## transcribe.py
- faster-whisper, model `small`, `word_timestamps=True`, VAD filter on.
- Output `transcript.json`:
```json
{
  "language": "en",
  "duration_s": 183.42,
  "words": [{"w": "Hello", "start": 0.32, "end": 0.61, "p": 0.98}],
  "segments": [{"text": "...", "start": 0.32, "end": 4.10}]
}
```
- Output `transcript.md`: timestamped readable transcript, one segment per line.

## vocal_metrics.py
Inputs: `audio.wav`, `transcript.json`. Output `vocal_metrics.json`:
```json
{
  "wpm_overall": 148.2,
  "wpm_by_minute": [152.0, 149.3],
  "filler": {"count": 11, "per_min": 3.6,
             "words": {"um": 6, "uh": 3, "like": 2},
             "timestamps": [12.4, 33.1]},
  "pauses": {
    "count": 24,
    "list": [{"start": 14.2, "dur": 1.6, "after_sentence_end": true,
              "bridged_by_filler": false}],
    "mean_dur": 0.7, "p90_dur": 1.4,
    "deliberate_count": 6, "anxious_gap_count": 9
  },
  "pitch": {"mean_hz": 118.3, "sd_hz": 22.1, "range_hz": [82, 190],
            "variance_score_0to100": 61,
            "sentence_final_drop_pct": 74},
  "intensity": {"mean_db": 62.1, "sd_db": 5.4,
                "trail_off_sentences_pct": 18},
  "steadiness": {"jitter_local_pct": 1.1, "shimmer_local_pct": 4.2}
}
```
Definitions:
- Pause = inter-word gap ≥ 0.5s. `after_sentence_end` from punctuation/segment
  boundary. `deliberate` heuristic: ≥ 0.8s AND at sentence/clause boundary AND
  not bridged by filler within 0.3s. `anxious_gap`: mid-clause ≥ 0.5s or any
  pause bridged by filler.
- Filler list: um, uh, er, ah, like (when non-comparative — approximate is fine),
  "you know", "sort of", "kind of", "I mean". Case-insensitive.
- `variance_score_0to100`: min-max scale pitch SD where SD 10 Hz→20 and
  SD 45 Hz→90 (linear, clamp 0–100). Crude but consistent session-to-session.
- Pitch via parselmouth (Praat autocorrelation, floor 60 Hz, ceiling 400 Hz);
  intensity via parselmouth; use librosa only for onset/energy extras.

## body_language.py
Skip cleanly (write `{"has_video": false}`) when input has no video stream.
Sample at 3 fps via OpenCV. MediaPipe Pose + Face Mesh with iris landmarks.
Output `body_metrics.json`:
```json
{
  "has_video": true,
  "frames_analyzed": 540,
  "posture": {
    "shoulder_forward_score_ts": [{"t": 0.0, "v": 0.82}],
    "uprightness_mean": 0.79, "uprightness_trend": "declining",
    "start_vs_end_delta": -0.11
  },
  "face": {
    "smile_pct": 34.2, "smile_ts": [{"t": 0.0, "v": 0.1}],
    "duchenne_available": false
  },
  "gaze": {
    "toward_camera_pct": 58.3,
    "down_pct": 21.0,
    "stability_score_0to100": 66,
    "note": "toward_camera_pct only meaningful for youtube/on-camera context"
  },
  "movement": {
    "head_velocity_mean": 0.03, "sway_score_0to100": 22,
    "gesture_active_pct": 41.0
  }
}
```
- Uprightness: shoulder line vs. hip line angle + ear-over-shoulder offset,
  normalized 0–1. Trend = linear fit sign over session.
- Smile: mouth-corner landmark ratio threshold; if py-feat installed, add
  AU6+AU12 Duchenne detection and set `duchenne_available: true`.
- Gaze: iris position relative to eye corners → toward-camera / left / right /
  down classification per frame.

## merge_timeline.py
Join everything on 1-second bins → `timeline.json`: for each second, speaking
(bool), wpm_local, pitch_sd_local, intensity, uprightness, smiling, gaze_class,
gesture_active. Then compute incongruence flags:
- `flat_face_while_storytelling`: segments where speech is continuous ≥ 10s and
  smile + pitch variance both in bottom quartile.
- `energy_body_mismatch`: intensity top quartile while gesture_active false and
  sway low ("talking big, standing dead") — flag with timestamps.
- `posture_collapse`: uprightness drops > 0.15 from session start.
Write flags with human-readable descriptions and timestamps.

## run_all.sh
`run_all.sh <media_file> <context>`
- Valid contexts: speech, small-talk, networking, dinner-party, youtube.
- Creates `analysis/<stem>/`, runs all stages in order, times each, skips video
  stages for audio-only input, prints a final summary block:
  packet path, duration, per-stage seconds, and "READY FOR COACHING REVIEW:
  read analysis/<stem>/ and rubrics/<context>.md".

# BUILD.md — Instructions for Claude Code to build this repo

You are bootstrapping the communications-coach pipeline. Work through the phases
in order. After each phase, run the listed verification before moving on. Commit
after every passing phase with a descriptive message.

## Phase 0 — Environment

1. Run `bash setup.sh`. Fix any failures (missing apt packages, pip conflicts)
   and update setup.sh so it runs cleanly from scratch — this file must remain
   the single source of truth for environment setup (it doubles as the Claude
   Code cloud environment setup script).
2. Verify: `python -c "import faster_whisper, parselmouth, librosa, mediapipe, cv2, numpy"`
   and `ffmpeg -version` all succeed.

## Phase 1 — Audio pipeline

Build these scripts per the specs in `pipeline/SPECS.md`:

1. `pipeline/extract_audio.sh` — ffmpeg: any input → 16kHz mono WAV in the
   analysis folder.
2. `pipeline/transcribe.py` — faster-whisper (model `small`, word timestamps on)
   → `transcript.json` (words with start/end) + `transcript.md` (readable).
3. `pipeline/vocal_metrics.py` — parselmouth + librosa + transcript.json →
   `vocal_metrics.json` per the schema in SPECS.md.

Verify: generate a 30-second test clip with ffmpeg + espeak (or record silence
plus a TTS voice), run all three scripts, confirm valid JSON output with sane
values (WPM between 60–220 on the TTS clip, pause list non-empty).

## Phase 2 — Video pipeline

4. `pipeline/body_language.py` — sample frames at 3 fps with OpenCV, run
   MediaPipe Pose + Face Mesh (+ iris), output `body_metrics.json` per SPECS.md.
   If MediaPipe wheels fail in this environment, document the fallback
   (mediapipe-silicon / opencv DNN pose) in this file and implement it.

   > **As built (2026-08):** mediapipe >= 1.0 removed the legacy `solutions`
   > API, so this script uses the Tasks API (`PoseLandmarker` +
   > `FaceLandmarker` with iris landmarks and blendshapes). The `.task` model
   > files are fetched by `setup.sh` into `pipeline/models/` (gitignored).
   > Bonus over the original spec: face blendshapes provide a Duchenne-smile
   > proxy (mouthSmile + cheekSquint), so `duchenne_available` is true without
   > py-feat.

Verify: run on any short video with a person in frame (download a CC0 talking-head
clip if none in `sessions/`); confirm posture/smile/gaze fields populate.

## Phase 3 — Merge + orchestration

5. `pipeline/merge_timeline.py` — join vocal + body metrics on a shared 1-second
   timeline → `timeline.json`, plus computed incongruence flags per SPECS.md.
6. `pipeline/run_all.sh <media_file> <context>` — orchestrates everything,
   creates `analysis/<stem>/`, prints a completion summary and the packet paths.
   Must be idempotent (safe to re-run) and must time each stage.

Verify: one command on a test file produces the full packet end-to-end in under
~2 minutes for a 3-minute clip.

## Phase 4 — Coaching loop

7. Write `docs/USAGE.md` for Kenny: how to add a session, the one command to
   run, how reports and score history work.
8. Create `reports/_TEMPLATE.md` implementing the report format from CLAUDE.md.
9. Create `analysis/score_history.py` — appends each report's context+score to
   `reports/score_history.csv` and can print a per-context trend table.

## Phase 5 — Dry run

10. Do one full rehearsal: pipeline on a test clip, then write a sample coaching
    report from the packet using `rubrics/speech.md`, save it to `reports/`,
    update score history. This proves the loop works before Kenny's first real
    session. Delete the sample report after committing the working pipeline,
    or clearly mark it SAMPLE.

## Standing rules while building

- Prefer boring, reliable libraries over clever ones.
- Every script: argparse CLI, docstring, graceful error message when a
  dependency or file is missing.
- Never analyze raw media directly in chat — always go through the pipeline.
- Keep processing fast: whisper `small`, 3 fps video sampling. Accuracy of
  timing matters more than transcription perfection.

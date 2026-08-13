#!/bin/bash
# SessionStart hook — get this container ready to score a recording fast.
#
# Two costs otherwise land on Kenny's FIRST upload of a session:
#   1. the ML stack install (~4-5 min on a fresh container)
#   2. a cold faster-whisper load, measured at ~42s vs ~2s warm
# Both are moved here, in the background, so they finish while he is still
# reading the scene and recording his response.
set -euo pipefail

echo '{"async": true, "asyncTimeout": 900000}'

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

# Idempotent: full setup only when something is actually missing.
need_setup=0
command -v ffmpeg >/dev/null 2>&1 || need_setup=1
python3 -c "import faster_whisper, parselmouth, cv2, mediapipe" >/dev/null 2>&1 || need_setup=1
[ -s pipeline/models/pose_landmarker_lite.task ] || need_setup=1
[ -s pipeline/models/face_landmarker.task ] || need_setup=1

if [ "$need_setup" -eq 1 ]; then
  echo "session-start: dependencies missing — running setup.sh"
  bash setup.sh
else
  echo "session-start: dependencies already present — skipping setup.sh"
fi

# Warm the whisper weights into the page cache even when setup.sh was skipped,
# so the first transcribe of the session is a warm load rather than a cold one.
python3 - <<'PY'
import os, time
try:
    from faster_whisper import WhisperModel
    t = time.time()
    WhisperModel("small", device="cpu", compute_type="int8",
                 cpu_threads=max(4, os.cpu_count() or 4))
    print(f"session-start: whisper 'small' warm in {time.time() - t:.1f}s")
except Exception as e:  # never fail the session over a warmup
    print(f"session-start: whisper warmup skipped ({e})")
PY

echo "session-start: ready — bash coach.sh <file> <context>"

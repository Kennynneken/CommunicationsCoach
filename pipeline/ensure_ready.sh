#!/usr/bin/env bash
# ensure_ready.sh — make this container ready to analyse a recording.
#
# Safe to call from anywhere, any number of times, concurrently. This is the
# ONLY thing that should ever invoke setup.sh: it takes an exclusive lock, so a
# second caller waits for the first to finish instead of starting a competing
# apt-get/pip run. The SessionStart hook and the coach both go through here.
#
#   bash pipeline/ensure_ready.sh          # set up if needed, then warm
#   bash pipeline/ensure_ready.sh --check  # report readiness, change nothing
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
LOCK="${TMPDIR:-/tmp}/commscoach-setup.lock"

is_ready() {
  command -v ffmpeg >/dev/null 2>&1 || return 1
  python3 -c "import faster_whisper, parselmouth, cv2, mediapipe" >/dev/null 2>&1 || return 1
  [ -s "$repo/pipeline/models/pose_landmarker_lite.task" ] || return 1
  [ -s "$repo/pipeline/models/face_landmarker.task" ] || return 1
  return 0
}

if [[ "${1:-}" == "--check" ]]; then
  if is_ready; then echo "ready"; exit 0; else echo "not-ready"; exit 1; fi
fi

# Fast path: already good, don't even take the lock.
if is_ready; then
  echo "ensure_ready: dependencies present"
else
  # If another process (typically the SessionStart hook) is mid-setup, this
  # blocks until it finishes rather than racing it.
  exec 9>"$LOCK"
  if ! flock -n 9; then
    echo "ensure_ready: another setup is in progress — waiting for it..."
    flock 9
  fi
  # Re-check inside the lock: the holder may have just finished the work.
  if is_ready; then
    echo "ensure_ready: setup completed by another process"
  else
    echo "ensure_ready: dependencies missing — running setup.sh"
    bash "$repo/setup.sh"
  fi
  exec 9>&-
fi

# Warm the whisper weights into page cache (~42s cold vs ~2s warm).
python3 - <<'PY'
import os, time
try:
    from faster_whisper import WhisperModel
    t = time.time()
    WhisperModel("small", device="cpu", compute_type="int8",
                 cpu_threads=max(4, os.cpu_count() or 4))
    print(f"ensure_ready: whisper 'small' warm in {time.time() - t:.1f}s")
except Exception as e:  # a cold model is slow, not fatal
    print(f"ensure_ready: whisper warmup skipped ({e})")
PY

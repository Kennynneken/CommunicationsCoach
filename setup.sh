#!/usr/bin/env bash
# Environment setup for the communications-coach pipeline.
# Also usable as the Claude Code cloud environment setup script.
set -euo pipefail

echo "== System packages =="
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y || apt-get update -y
  sudo apt-get install -y ffmpeg espeak-ng libsndfile1 || \
    apt-get install -y ffmpeg espeak-ng libsndfile1
fi

echo "== Python packages =="
# pip may be distro-managed (RECORD file missing) — a failed self-upgrade is fine.
python3 -m pip install --upgrade pip 2>/dev/null || echo "pip self-upgrade skipped (distro-managed); continuing with $(python3 -m pip --version)"
python3 -m pip install \
  faster-whisper \
  praat-parselmouth \
  librosa \
  soundfile \
  numpy \
  pandas \
  mediapipe \
  opencv-python-headless

# Optional, heavier: facial action units (Duchenne vs. social smile).
# Uncomment when Phase 2 is stable — it pulls torch.
# python3 -m pip install py-feat
# (mediapipe >= 1.0 face-landmarker blendshapes already give a Duchenne proxy —
#  mouthSmile + cheekSquint — so py-feat is only needed for research-grade AUs.)

echo "== MediaPipe task models =="
# mediapipe >= 1.0 removed the bundled legacy `solutions` API; the Tasks API
# needs these model files. Downloaded once, cached in pipeline/models/.
MODELS_DIR="$(cd "$(dirname "$0")" && pwd)/pipeline/models"
mkdir -p "$MODELS_DIR"
MP_BASE="https://storage.googleapis.com/mediapipe-models"
[[ -s "$MODELS_DIR/pose_landmarker_lite.task" ]] || \
  curl -sSL -o "$MODELS_DIR/pose_landmarker_lite.task" \
    "$MP_BASE/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
[[ -s "$MODELS_DIR/face_landmarker.task" ]] || \
  curl -sSL -o "$MODELS_DIR/face_landmarker.task" \
    "$MP_BASE/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
ls -la "$MODELS_DIR"

echo "== Whisper model (pre-download + warm) =="
# Without this the FIRST take of every fresh container pays the model download
# and a cold load inside the pipeline run — measured at ~42s versus ~2s warm.
# Pulling it here moves that cost into environment setup, where nobody is
# waiting on a score.
python3 - <<'EOF'
import os, time
from faster_whisper import WhisperModel
t = time.time()
WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=max(4, os.cpu_count() or 4))
print(f"whisper 'small' ready in {time.time() - t:.1f}s")
EOF

echo "== Verify =="
ffmpeg -version | head -n1
python3 - <<'EOF'
import faster_whisper, parselmouth, librosa, numpy, cv2
try:
    import mediapipe
    print("mediapipe OK")
except Exception as e:
    print("WARNING: mediapipe failed to import:", e)
    print("See BUILD.md Phase 2 fallback notes.")
print("Core audio stack OK")
EOF

echo "Setup complete."

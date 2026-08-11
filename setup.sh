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
python3 -m pip install --upgrade pip
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

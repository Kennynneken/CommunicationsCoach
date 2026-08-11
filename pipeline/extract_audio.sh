#!/usr/bin/env bash
# extract_audio.sh <media_file> <outdir>
# ffmpeg: any input -> <outdir>/audio.wav (16 kHz mono pcm_s16le)
# Also writes <outdir>/media_info.json (duration, has_video, resolution, fps).
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: extract_audio.sh <media_file> <outdir>" >&2
  exit 2
fi
in="$1"; outdir="$2"
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not found — run setup.sh first." >&2
  exit 1
fi
if [[ ! -f "$in" ]]; then
  echo "ERROR: input file not found: $in" >&2
  exit 1
fi
mkdir -p "$outdir"

ffmpeg -y -loglevel error -i "$in" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$outdir/audio.wav"

ffprobe -v error -print_format json -show_format -show_streams "$in" > "$outdir/.ffprobe.json"
python3 - "$outdir" <<'EOF'
import json, sys, os
outdir = sys.argv[1]
with open(os.path.join(outdir, ".ffprobe.json")) as f:
    probe = json.load(f)
video = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"
              and s.get("disposition", {}).get("attached_pic", 0) == 0), None)
fps = None
if video and video.get("avg_frame_rate") not in (None, "0/0"):
    num, _, den = video["avg_frame_rate"].partition("/")
    if den and float(den) != 0:
        fps = round(float(num) / float(den), 2)
info = {
    "duration_s": round(float(probe.get("format", {}).get("duration", 0.0)), 2),
    "has_video": video is not None,
    "resolution": f'{video["width"]}x{video["height"]}' if video else None,
    "fps": fps,
}
with open(os.path.join(outdir, "media_info.json"), "w") as f:
    json.dump(info, f, indent=2)
os.remove(os.path.join(outdir, ".ffprobe.json"))
print(f'media_info: {info}')
EOF

echo "audio extracted -> $outdir/audio.wav"

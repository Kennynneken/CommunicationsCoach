#!/usr/bin/env bash
# run_all.sh <media_file> <context>
# Orchestrates the full analysis pipeline into analysis/<stem>/.
# Idempotent: re-running overwrites the packet for that file. Times each stage.
set -euo pipefail

CONTEXTS="speech small-talk networking dinner-party youtube"

if [[ $# -ne 2 ]]; then
  echo "usage: run_all.sh <media_file> <context>" >&2
  echo "contexts: $CONTEXTS" >&2
  exit 2
fi
media="$1"; context="$2"

if [[ ! -f "$media" ]]; then
  echo "ERROR: media file not found: $media" >&2
  exit 1
fi
if ! grep -qw -- "$context" <<<"$CONTEXTS"; then
  echo "ERROR: unknown context '$context' (valid: $CONTEXTS)" >&2
  exit 1
fi

repo="$(cd "$(dirname "$0")/.." && pwd)"
pipe="$repo/pipeline"
stem="$(basename "$media")"; stem="${stem%.*}"
outdir="$repo/analysis/$stem"
mkdir -p "$outdir"
echo "$context" > "$outdir/context.txt"

declare -a stage_names stage_secs
run_stage() {
  local name="$1"; shift
  local t0 t1
  t0=$(date +%s.%N)
  "$@"
  t1=$(date +%s.%N)
  stage_names+=("$name")
  stage_secs+=("$(printf '%.1f' "$(echo "$t1 - $t0" | bc)")")
}

echo "== [1/4] extract_audio =="
run_stage extract_audio bash "$pipe/extract_audio.sh" "$media" "$outdir"

echo "== [2/4] transcribe =="
run_stage transcribe python3 "$pipe/transcribe.py" --input "$outdir/audio.wav" --outdir "$outdir"

echo "== [3/4] vocal_metrics =="
run_stage vocal_metrics python3 "$pipe/vocal_metrics.py" --input "$outdir/audio.wav" --outdir "$outdir"

echo "== [4/4] body_language + merge =="
has_video=$(python3 -c "import json;print(json.load(open('$outdir/media_info.json'))['has_video'])")
if [[ "$has_video" == "True" ]]; then
  run_stage body_language python3 "$pipe/body_language.py" --input "$media" --outdir "$outdir"
else
  echo "audio-only input — skipping video analysis"
  printf '{\n  "has_video": false\n}\n' > "$outdir/body_metrics.json"
fi
run_stage merge_timeline python3 "$pipe/merge_timeline.py" --outdir "$outdir"

duration=$(python3 -c "import json;print(json.load(open('$outdir/media_info.json'))['duration_s'])")

echo
echo "================= PIPELINE COMPLETE ================="
echo "packet:    $outdir"
echo "media:     $media (${duration}s, video: $has_video)"
echo "context:   $context"
echo "stages:"
for i in "${!stage_names[@]}"; do
  printf '  %-16s %6ss\n' "${stage_names[$i]}" "${stage_secs[$i]}"
done
echo
echo "READY FOR COACHING REVIEW: read analysis/$stem/ and rubrics/$context.md"
echo "====================================================="

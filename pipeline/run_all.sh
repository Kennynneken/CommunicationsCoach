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

# body_language reads the video directly and shares no state with the audio
# stages, so it runs alongside transcribe instead of waiting behind it. On a
# short clip that hides the whole video pass inside the whisper pass.
has_video=$(python3 -c "import json;print(json.load(open('$outdir/media_info.json'))['has_video'])")
body_pid=""
if [[ "$has_video" == "True" ]]; then
  echo "== [2/4] body_language (background, parallel with transcribe) =="
  body_t0=$(date +%s.%N)
  python3 "$pipe/body_language.py" --input "$media" --outdir "$outdir" \
    >"$outdir/.body.log" 2>&1 &
  body_pid=$!
else
  echo "audio-only input — skipping video analysis"
  printf '{\n  "has_video": false\n}\n' > "$outdir/body_metrics.json"
fi

echo "== [3/4] transcribe + vocal_metrics =="
run_stage transcribe python3 "$pipe/transcribe.py" --input "$outdir/audio.wav" --outdir "$outdir"
run_stage vocal_metrics python3 "$pipe/vocal_metrics.py" --input "$outdir/audio.wav" --outdir "$outdir"

if [[ -n "$body_pid" ]]; then
  # Surface a video-stage failure instead of letting merge read a stale packet.
  if ! wait "$body_pid"; then
    echo "ERROR: body_language failed —" >&2
    cat "$outdir/.body.log" >&2
    exit 1
  fi
  cat "$outdir/.body.log"; rm -f "$outdir/.body.log"
  stage_names+=("body_language*"); stage_secs+=("$(printf '%.1f' "$(echo "$(date +%s.%N) - $body_t0" | bc)")")
fi

echo "== [4/4] merge =="
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
[[ -n "$body_pid" ]] && echo "  (* ran in parallel with transcribe — not additive to wall clock)"
echo
python3 "$pipe/digest.py" --outdir "$outdir"
echo
echo "READY FOR COACHING REVIEW: full packet in analysis/$stem/, rubric rubrics/$context.md"
echo "Score the 8 dimensions in rubrics/dimensions.md; patterns in coaching/kenny-patterns.md"
echo "====================================================="

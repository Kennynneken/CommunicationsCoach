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

# If the SessionStart hook is still installing the environment, wait for it.
lock="$repo/.claude/.setup-running"
if [[ -e "$lock" ]]; then
  echo "environment setup still running (SessionStart hook) — waiting..."
  waited=0
  while [[ -e "$lock" && $waited -lt 600 ]]; do sleep 2; waited=$((waited+2)); done
  if [[ -e "$lock" ]]; then
    echo "ERROR: setup still not finished after ${waited}s — check .claude/setup.log" >&2
    exit 1
  fi
  echo "setup finished after ~${waited}s"
fi
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

echo "== [1/3] extract_audio =="
run_stage extract_audio bash "$pipe/extract_audio.sh" "$media" "$outdir"

# The audio chain (transcribe -> vocal_metrics, which reads transcript.json)
# and body_language are independent — run the two concurrently so wall clock
# is the slowest chain, not the sum of all stages.
echo "== [2/3] (transcribe -> vocal_metrics) + body_language (parallel) =="
has_video=$(python3 -c "import json;print(json.load(open('$outdir/media_info.json'))['has_video'])")

t0=$(date +%s.%N)
{
  python3 "$pipe/transcribe.py" --input "$outdir/audio.wav" --outdir "$outdir" \
    > "$outdir/.transcribe.log" 2>&1 &&
  python3 "$pipe/vocal_metrics.py" --input "$outdir/audio.wav" --outdir "$outdir" \
    > "$outdir/.vocal.log" 2>&1
} & apid=$!
bpid=""
if [[ "$has_video" == "True" ]]; then
  python3 "$pipe/body_language.py" --input "$media" --outdir "$outdir" \
    > "$outdir/.body.log" 2>&1 & bpid=$!
else
  echo "audio-only input — skipping video analysis"
  printf '{\n  "has_video": false\n}\n' > "$outdir/body_metrics.json"
fi

fail=0
wait "$apid" || { echo "ERROR: audio chain (transcribe/vocal_metrics) failed:" >&2
                  cat "$outdir/.transcribe.log" "$outdir/.vocal.log" >&2 2>/dev/null; fail=1; }
if [[ -n "$bpid" ]]; then
  wait "$bpid" || { echo "ERROR: body_language failed:" >&2; cat "$outdir/.body.log" >&2; fail=1; }
fi
[[ "$fail" == 0 ]] || exit 1
t1=$(date +%s.%N)
stage_names+=("analyze (parallel)")
stage_secs+=("$(printf '%.1f' "$(echo "$t1 - $t0" | bc)")")
grep -h -v '^\(INFO\|WARNING\|W[0-9]\)' "$outdir"/.transcribe.log "$outdir"/.vocal.log \
  "$outdir"/.body.log 2>/dev/null || true
rm -f "$outdir"/.transcribe.log "$outdir"/.vocal.log "$outdir"/.body.log

echo "== [3/3] merge_timeline =="
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

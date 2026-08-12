#!/usr/bin/env bash
# coach.sh <media_file> [context] [--name <slug>]
#
# One command from a recording anywhere on disk to a scored-ready digest:
# copies the file into sessions/ with a dated name, runs the pipeline, and
# prints the coaching digest. Use this instead of copying by hand and then
# calling run_all.sh — it is one round trip instead of three.
#
#   bash coach.sh ~/uploads/video.MOV networking --name s5-big-fish-take1
#
# context defaults to networking. Valid: speech small-talk networking
# dinner-party youtube.
set -euo pipefail

repo="$(cd "$(dirname "$0")" && pwd)"
src="${1:-}"; context="${2:-networking}"; slug=""

if [[ -z "$src" ]]; then
  echo "usage: coach.sh <media_file> [context] [--name <slug>]" >&2
  exit 2
fi
shift $(( $# > 1 ? 2 : 1 ))
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) slug="${2:-}"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -f "$src" ]]; then
  echo "ERROR: no such file: $src" >&2
  exit 1
fi

ext="${src##*.}"
date_prefix="$(date +%F)"
if [[ -z "$slug" ]]; then
  base="$(basename "$src")"; slug="${base%.*}"
fi
dest="$repo/sessions/${date_prefix}-${slug}.${ext}"

# Never silently clobber a previous take of the same name — auto-suffix instead.
if [[ -e "$dest" ]]; then
  n=2
  while [[ -e "$repo/sessions/${date_prefix}-${slug}-v${n}.${ext}" ]]; do n=$((n+1)); done
  dest="$repo/sessions/${date_prefix}-${slug}-v${n}.${ext}"
  echo "note: name taken, using $(basename "$dest")"
fi

cp "$src" "$dest"
echo "ingested -> sessions/$(basename "$dest")"
exec bash "$repo/pipeline/run_all.sh" "sessions/$(basename "$dest")" "$context"

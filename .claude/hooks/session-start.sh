#!/bin/bash
# SessionStart hook — get this container ready to score a recording.
#
# SYNCHRONOUS on purpose. An earlier async version started setup.sh in the
# background, the agent began before it finished, saw missing dependencies and
# launched a second competing setup. Blocking here is the only way to guarantee
# the session starts ready.
#
# Cost when the container is already provisioned: ~3s (a whisper warmup).
# Cost on a genuinely fresh container: the full install, ~4-5 min. If that is
# happening every session, point the Claude Code environment's setup script at
# this repo's setup.sh so the provisioned image is cached WITH the dependencies
# — see docs/USAGE.md, "Why is my container coming up empty?".
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"
bash pipeline/ensure_ready.sh
echo "session-start: ready — bash coach.sh <file> <context>"

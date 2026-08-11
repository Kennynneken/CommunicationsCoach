#!/bin/bash
# SessionStart hook: install the analysis-pipeline environment (apt + pip +
# whisper/mediapipe models) in the background so the pipeline is ready by the
# time a recording is uploaded. Remote (Claude Code on the web) only.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Async: don't block session start — setup takes ~3 min on a cold container.
# run_all.sh waits on the lock file below, so the race is handled.
echo '{"async": true, "asyncTimeout": 600000}'

cd "$CLAUDE_PROJECT_DIR"
LOCK=".claude/.setup-running"
LOG=".claude/setup.log"
mkdir -p .claude
touch "$LOCK"
trap 'rm -f "$LOCK"' EXIT

# setup.sh is idempotent; on a cached container this completes in seconds.
bash setup.sh > "$LOG" 2>&1
echo "session-start setup complete" >> "$LOG"

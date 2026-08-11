# Communications Coach — Kenny Aronson

A Claude Code-powered coaching system: drop in a recording of a speech,
conversation, or on-camera take; a local pipeline extracts objective vocal and
body-language metrics; Claude scores the delivery (1–100, calibrated to
world-class historic levels) against a context-specific rubric and returns one
specific drill for the next round.

## First run (bootstrapping)

1. Push this repo to GitHub and open it in Claude Code (cloud). Point the
   environment setup at `setup.sh`.
2. First message to Claude Code:
   > Read CLAUDE.md, then execute BUILD.md phase by phase until the dry run
   > in Phase 5 passes. Commit after each phase.
3. Claude Code builds and verifies the whole pipeline itself.

## Every session after that

1. Add a recording to `sessions/` (video or audio; name it descriptively,
   e.g. `2026-08-14-wedding-toast-take2.mp4`).
2. Tell Claude Code: `Coach me: sessions/<file>, context: speech`
   (contexts: speech, small-talk, networking, dinner-party, youtube)
3. Read your report in `reports/`. Drill THE ONE THING. Record the next take.

## Layout

- `CLAUDE.md` — the coach's identity, principles, scale, and report format
- `BUILD.md` — self-build instructions (phased, with verification gates)
- `setup.sh` — full environment setup (also the cloud env setup script)
- `pipeline/SPECS.md` — exact specs for every pipeline module
- `rubrics/` — per-context scoring rubrics
- `sessions/` → `analysis/` → `reports/` — the data flow

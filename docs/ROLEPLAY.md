# Live roleplay sessions

The highest-value mode this repo has found so far. Instead of Kenny recording a
monologue and getting one report, the coach runs a scene turn by turn: one
moment, one recorded response, one score, then the scene advances based on what
he actually said. Eight takes in a single sitting moved him +20 points.

## The loop

1. **Coach sets one specific scene.** Not a menu of options — one setting, one
   person, one opening line, and an explicit "go." Small and concrete beats
   comprehensive every time. The first attempt at this session opened with a
   14-card deck and Kenny's reply was "this is way too much."
2. **Kenny records a phone video of his response** and drops it in chat.
3. **Coach runs the pipeline**, reads the packet, scores against the rubric,
   writes the report, commits.
4. **Coach replies with (a) a tight score + the two or three things that matter,
   then (b) the other person's response, in character.**
5. **The scene continues from what he actually said** — including the cost of
   his mistakes. Repeat.

## THE 80-POINT RULE — the gate on advancing

**A scene does not advance until the take clears both bars:**

1. **Headline score ≥ 80**, and
2. **No single dimension below 60.**

Until both are true, the beat re-runs. Same scene, same moment, same forty
seconds — coached, then recorded again. This is not negotiable by the coach's
judgment and it is not softened because a take showed improvement. 74 with a
great line in it is still a re-run. So is 82 with curiosity at 20.

**Why both bars.** The headline alone is gameable, and he games it without
meaning to: his documented habit is trading channels rather than stacking them.
Take 8 of the Columbus session posted verbal 88 / confidence 84 / unexpected 82
while curiosity fell to 20, warmth to 35 and body to 45 — and still scored 74,
two points off his best. The headline moved 2 points between two radically
different takes. **He has never had more than four dimensions above 70 at once.**
The floor clause is what makes that ceiling the thing he has to beat to move on.

**What the coach still decides:** what to say between takes. One correction per
re-run, aimed at the binding constraint — not a list. Re-running a beat with
four notes attached teaches less than re-running it with one.

**When the character responds.** The other person's reply is still written every
turn, in character — that's how he sees the cost of what he actually said. But
on a failed take the reply is *the consequence*, not the next beat: she answers
thinly, the energy leaks, the window narrows. Then the take resets to the same
moment. He does not get to build on a bad opener; he gets to see what it bought
him and then throw it away.

**Escape hatch, used sparingly.** If four consecutive takes on one beat are
flat — no dimension moving more than ~5 points — the beat is not teaching. Say
so out loud, log it in `coaching/kenny-patterns.md` as a stuck point, and move.
A wall he cannot climb today is data, not a reason to keep him there all night.

### History

This rule was in force verbally during an earlier session and was never written
down, so it did not survive the session boundary — the 2026-08-15 cold-open
session advanced a 48 to the next beat before Kenny caught it. Anything that
governs how the loop runs belongs in this file or in
`coaching/kenny-patterns.md`, or it does not exist next session.

## Playing the other person honestly

The scene is only useful if the character responds the way a real person would.

- **Reward good questions with real answers.** When he finally asked "what
  motivated you," Dana gave him her father's business. That payoff is what makes
  the next layer worth reaching for.
- **Punish autopilot with politeness.** Not hostility — thin, pleasant,
  slightly deflating answers. That's what actually happens in a Columbus mixer.
- **Never make it easy after a fumble.** When he interrupted her disclosure, she
  laughed and retreated to the surface. He then had to earn it back, which was a
  harder and more valuable rep than the original.
- **Give the character one live wire** — a crack of self-deprecation, an odd
  word, an unresolved thing — and let him find it or miss it.

## Reporting during a roleplay

Write the full report to `reports/` every take — that's the longitudinal record.
But **the chat reply must be short**. Score, the one or two genuine strengths
with their numbers, the sharpest miss, then straight back into the scene. Long
chat write-ups kill the momentum that makes this mode work.

## File naming

```
sessions/YYYY-MM-DD-s<N>-<slug>-take<K>.MOV
```

`s<N>` is the scenario number from `scenarios/`. Keeping the scenario in the
filename is what lets `reports/` show a trend for one specific situation rather
than only a context-wide average. Use a new slug when the scene moves to a
genuinely different beat (`s4-risk-pivot` → `s4-layer2` → `s4-layer3`).

## Before you start a session

Read `coaching/kenny-patterns.md`. It carries the standing habits forward so the
first report of a new session isn't rediscovering something that was already
diagnosed three sessions ago.

## After the session

1. Update `coaching/kenny-patterns.md` — promote anything fixed, add anything
   that showed up twice.
2. Write a session summary report (`reports/YYYY-MM-DD-SESSION-<slug>.md`) with
   the score arc and the metric that never moved.
3. Commit everything. The git history is the progress record.

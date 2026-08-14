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

## The coach's judgment call each turn

After each take, choose one:

- **Coach the moment and re-run it** — when he missed something fundamental and
  repeating the same beat teaches more than moving on.
- **Advance the scene and let the cost land** — usually better. If he asked a
  logistics question, the character answers thinly and the energy visibly leaks.
  If he interrupted a disclosure, the character takes the exit he handed her and
  the thread closes. Consequences teach faster than instructions.

Advance by default. Re-run only when the miss would compound.

**Mastery mode (added 2026-08-14, per Kenny):** when invoked, the scene
freezes and the SAME beat is re-drilled — same setup, same incoming line —
until the take scores **80 or higher**. The other person's line does not
change between attempts; only Kenny's response does. Score each attempt
normally (full report, history logged, `-takeN` increments), chat reply stays
score + ONE THING + "again" or "passed." The bar is the headline score for
the beat, not a single dimension. On a pass, the scene resumes from the
passing take's version of events.

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
But **the chat reply must be minimal** (per Kenny, 2026-08-14): **score, THE
ONE THING for the next take, then the scene. Nothing else.** No strengths
list, no secondary fixes, no metric tour — all of that lives in the written
report for later reading. One correction per shot is the one-element rule
(Giang) applied to the feedback channel itself: a list of five fixes produces
zero fixes. If a previous ONE THING was executed, it may be acknowledged in
one clause, then replaced.

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

# Session Summary — 2026-08-11 — Columbus Chamber Mixer Roleplay

**Context:** networking · **8 takes** · live roleplay, one scene carried
end to end: approaching Dana Whitfield (Nationwide) at the rail at a Chamber
after-hours at Land-Grant, Franklinton.

**Score arc: 54 → 57 → 63 → 66 → 71 → 72 → 76 → 74 (+20 net, peak 76)**

| # | Take | Beat | Score |
|---|---|---|---|
| 1 | `s1-dana-rail-take1` | Her opener: "pretending to look for someone" | 54 |
| 2 | `s1-dana-rail-take2` | Recovering after a flat logistics answer | 57 ↑3 |
| 3 | `s3-what-do-you-do-take1` | "So what do you do?" | 63 ↑6 |
| 4 | `s4-risk-pivot-take1` | Her category answer + self-deprecating crack | 66 ↑3 |
| 5 | `s4-layer2-take1` | Her father's business, "embarrassingly recently" | 71 ↑5 |
| 6 | `s4-layer3-take1` | She retreats to the surface — get her back | 72 ↑1 |
| 7 | `s4-layer3-take2` | Her disclosure: "I've never said that out loud" | 76 ↑4 |
| 8 | `s12-exit-take1` | She lifts and compliments him | 74 ↓2 |

## Dimension profile (backfilled)

Eight-dimension scoring (`rubrics/dimensions.md`) was added to the system after
this session and backfilled across all eight takes from the packets and
transcripts. Rows are takes 1–8.

| Dimension | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | avg |
|---|---|---|---|---|---|---|---|---|---|
| Confidence | 42 | 60 | 62 | 66 | 72 | 80 | 55 | **84** | 65 |
| Warmth | 62 | 66 | 65 | 48 | **74** | 62 | 58 | 35 | 59 |
| Body language | 68 | 62 | 72 | 74 | 70 | 66 | **82** | 45 | 67 |
| Presence | 30 | 25 | 45 | 55 | 35 | 48 | **78** | 42 | **45** |
| Verbal acuity | 58 | 52 | 55 | 60 | 66 | 58 | 50 | **88** | 61 |
| Unexpectedness | 55 | 58 | 70 | 45 | 62 | 78 | 52 | **82** | 63 |
| Curiosity | 25 | 22 | 30 | 78 | 85 | 70 | **90** | 20 | 52 |
| Attunement | 45 | 40 | 55 | 62 | 38 | 68 | **84** | 38 | 54 |
| **HEADLINE** | 54 | 57 | 63 | 66 | 71 | 72 | **76** | 74 | 67 |

- **Bottleneck: Presence, avg 45** — only one take above 55, and that one scored
  on a held breath *before* speaking rather than a pause inside it. The
  dimension model found the same problem the pause map did, independently.
- **Lowest ceiling: Warmth, best-ever 74.** Every other dimension has cleared 78
  at least once. Warmth never has. Quietest problem in the profile.
- **He trades channels rather than stacking them.** Take 8: verbal 88,
  confidence 84, unexpectedness 82 — while curiosity fell to 20, warmth to 35,
  attunement to 38, body to 45. Take 7 is the mirror image. **Never more than
  four dimensions above 70 simultaneously.** That is the real ceiling, and it is
  invisible in the headline score, which moved only 2 points between those two
  radically different takes.

## The arc in one paragraph

He started by burning a charming opening line on event logistics — three
consecutive questions about the mixer itself — and finished by reaching a
genuine third layer with a stranger, in about ninety seconds of cumulative
speech. The turning point was take 4, where he ran "what motivated you" instead
of the résumé question; everything after that was Dana giving him progressively
more, and him mostly not dropping it. The one take that went backwards (8) went
backwards on *body*, not words: he produced the best line of the session while
his posture collapsed 0.12 and his sway doubled.

## What genuinely changed

- **Filler: 11.1 → 0.0 per minute.** Four consecutive clean takes, including
  under the heaviest emotional moment of the night. Fixed inside one session.
- **Question quality: logistics → motivation → interior.** Take 1 asked how she
  found out about the event. Take 7 asked what was going through her mind in the
  car. That is the entire distance the small-talk rubric measures.
- **Sentence-final certainty: 0% → 100%** by take 2, mostly held after.
- **The padding habit, broken on take 8.** Seven takes of attaching a clause to
  every good line, then eleven clean words with nothing on either end.
- **He gave his name (take 5) and started using hers (take 6).**

## What never moved

- **Zero deliberate pauses. Eight takes, eight zeros.** Never once held 0.8s+ of
  silence inside his own speech. Closest: 0.76s.
- **Tempo. And this was measured wrong for most of the session — see below.**

## Correction: the tempo story in reports 3, 7 and 8 was wrong

At wrap I added a `wpm_speaking` metric to the pipeline (articulation rate, with
lead-in, lead-out and pauses removed) after noticing in take 4 that a headline
of 156 WPM was hiding a real speaking rate of ~240. Recomputed across all eight
takes:

| Take | wpm_overall (reported) | wpm_speaking (true) | lead-in |
|---|---|---|---|
| 1 | 177.9 | **218.2** | 0.88s |
| 2 | 233.4 | **264.4** | 0.34s |
| 3 | 141.8 | **176.3** | 0.62s |
| 4 | 156.3 | **249.3** | 3.09s |
| 5 | 199.0 | **246.4** | 0.66s |
| 6 | 154.0 | **214.3** | 1.23s |
| 7 | 123.3 | **192.9** | 2.45s |
| 8 | 121.8 | **222.2** | 1.33s |

`218 → 264 → 176 → 249 → 246 → 214 → 193 → 222`. **No trend.** He never entered
the 110–150 power zone. The reports for takes 3, 7 and 8 credited him with
slowing down; that credit was an artifact of silence at the edges of short
clips, and correction notes have been added to each. Scores stand as recorded —
they're the historical log — but composure was over-credited in takes 7 and 8,
and **tempo is now the top open item, undrilled.**

The pre-turn holds those lead-in figures represent are real and remain a genuine
strength (3.09s and 2.45s, with posture *rising* through them). The error was
reading a held breath as a slowed sentence.

## Best moment of the session

**Take 7, 00:02 — "What was going through your mind in that moment?"** asked
after two and a half seconds of held silence at 0.99 uprightness, with a
correctly serious face, zero fillers, and 57% gesture activity. She answered
with something she said she'd never said out loud. That question is the whole
point of the small-talk and networking rubrics and he found it live.

## Best line of the session

**Take 8 — "I don't try to be good. I try to be real."** Eleven words,
antithesis, both halves closing downward, no padding. Wasted by a body that
folded while saying it.

## THE ONE THING for next session

**One deliberate pause. 0.8 seconds or longer, at a sentence end, inside your
speech — not before it.** Current: 0 across 8 takes, with a true articulation
rate of 193–264 WPM that has never touched the power zone. The drill: after any
sentence that completes an idea, close your mouth and count *one-one-thousand*
before the next one starts. Everything else on the open list — the padding
clause, the stacked questions, the minimizers — is downstream of talking too
fast to hear yourself.

Next session opens with `coaching/kenny-patterns.md`.

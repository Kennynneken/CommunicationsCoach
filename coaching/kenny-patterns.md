# Standing Patterns — Kenny

Longitudinal tells carried across sessions, so each new session starts informed
instead of rediscovering the same habits. **Read this before writing any report.**
Update it at the end of every session: promote a fixed habit to *Resolved*, add
anything that shows up twice.

Last updated: 2026-08-14 (cold-approach drill, 3 takes + research rebuild)

**2026-08-14 framework note:** the grading system was rebuilt against the
research corpus (`coaching/research-foundations.md`). Several standing items
below were *reframed* by it — the reframes are marked inline. Biggest changes:
tempo is now scored as contrast-not-zone (his 210–260 WPM is workable IF
varied and punctuated — RDJ profile), pure question-asking now caps curiosity
(needs the disclosure braid), warmth is scored on smile *timing*, gesture 0%
is now a scored deficit, and cold approaches are scored on Smithyman's
stranger→non-stranger goal, not brilliance.

---

## Dimension profile (8 takes, `rubrics/dimensions.md`)

`python3 analysis/score_history.py --dimensions`

| Dimension | avg | best | worst | Read |
|---|---|---|---|---|
| Body language | **67** | 82 | 45 | Steadiest channel. Upright and still by default. |
| Confidence | **65** | 84 | 42 | Climbed hard all session; now a strength. |
| Unexpectedness | **63** | 82 | 45 | Spiky and real — the RDJ axis is genuinely available to him. |
| Verbal acuity | **61** | 88 | 50 | All-or-nothing: one 88, everything else 50–66. |
| Warmth | **59** | **74** | 35 | **Lowest ceiling of all eight — never once been warmer than 74.** |
| Attunement | **54** | 84 | 38 | Wildly volatile; swings 46 points take to take. |
| Curiosity | **52** | 90 | 20 | The widest range in the profile (70 points). |
| Presence | **45** | 78 | 25 | **The bottleneck.** Only one take above 55. |

Three structural facts this exposes:

1. **Presence is the bottleneck** (avg 45), and the tool found it independently
   of the pause analysis. Everything else is downstream of talking too fast to
   hear himself.
2. **Warmth has the lowest ceiling** (74). Every other dimension has cleared 78
   at least once; warmth never has. He is *capable* of warmth — Duchenne
   proportion is 84–100% — but he has never sustained it through a whole take.
   This is the quietest problem in the profile and probably the most important
   one after presence.
3. **He trades channels instead of stacking them.** Take 8 posted verbal 88 /
   confidence 84 / unexpected 82 while curiosity fell to 20, warmth to 35,
   attunement to 38 and body to 45. Take 7 was the inverse: curiosity 90 /
   attunement 84 / body 82 / presence 78, with verbal at 50. **He has never had
   more than four dimensions above 70 at once.** That, not the headline score,
   is the ceiling to attack.

---

## Open — actively drilling

### 0a. The chassis fails at length (named 2026-08-14, cold-take5)
Every take longer than ~10s in the record shows posture decline; take5 is the
worst yet (0.90 → 0.77, −0.13, sway 35 — both records) with the collapse
monotonic through the take. Short takes hide it: takes 1–4 today were 4–7s.
Cross-reference mixer take 8 (best line of the night, body folding while
saying it). The body has never yet survived a full paragraph.

### 0. The late smile (promoted to top open item, 2026-08-14)
His warmest expression reliably arrives AFTER he finishes speaking. Measured
across five occurrences (s1, s4-risk, s4-layer3-1, both 08-14 cold takes):
smile high on throwaway openers, 0.00 across the payload line, then peaks
(0.80–0.82, his best values ever) ~0.4s after the last word. Duchenne is 100%
— the warmth is real, it is a *timing* failure: the face works while he talks
and releases when done. Research frame: tonality follows the face (Giang), so
the warm line is being delivered with cold tone every time. **Fix showed up
immediately when drilled** (take 3: smile led the first word by 0.04s and
warmth posted his best-ever 60) — but it held only on the open, then strobed
off on every content word. Drill: A4 smile-then-speak; last word gets more
face than the first.

### 0b. The buried question (named 2026-08-14)
He asks, then answers or talks over his own silence — 0.64s from question to
self-rescue in the take that exposed it. Related: stacked questions (below).
The question's entire value is in the space after it. Drill: S1 ask-then-shut-up
— the recording must end in his silence.

### 1. The padding clause (the defining habit) — now understood as a safety behavior
He cannot let a good line stand alone. Every strong sentence gets a second
sentence that explains, softens, tags, or labels it. Research reframe
(Smithyman): this is a textbook **safety behavior** — pre-softening judgment.
It raises anxiety and blocks connection; the fix is exposure (leave the line
naked), which he has already done once under load (s12).

| Take | The good line | The padding |
|---|---|---|
| s3 | "Oh, I'm up to no good. That's what I do." | *"Jokes aside…"* |
| s4-layer2 | "Why do you say it was embarrassing?" | *8-second name introduction* |
| s4-layer3-1 | "Let's take this back somewhere real." | *"…shall we?"* |
| s4-layer3-2 | "What was going through your mind?" | *"That must have been eye-opening"* (moved to the front) |

Note the migration in the last row — when told to stop adding a clause *after*,
he added one *before*. The instinct is the target, not the position.
**First fully clean take: s12-exit ("I don't try to be good. I try to be real.")
— 11 words, nothing attached. It is the best line of the session. Not a
coincidence.**

### 2. Zero deliberate pauses — 11 for 11
`deliberate_count = 0` in every take recorded to date; the three 08-14 takes
had **zero silence of any kind inside them** (talking Ns of Ns span). Research
reframe: no expert prescribes a pause duration — the 0.8s bar is our
instrument, not doctrine. What's actually broken is pause *function*: he never
leaves space after his own questions and never slows into a key line. Keep
measuring `deliberate_count`; coach S1/S3, not the stopwatch.

### 3. Tempo — reframed 2026-08-14: contrast, not zone
`wpm_speaking` across 11 takes:
`218 → 264 → 176 → 249 → 246 → 214 → 193 → 222 → 209 → 216 → 232`
No trend, and **no longer chasing 110–150 in conversation** — research says
score contrast, and fast-with-melody-and-pauses is a legitimate elite profile
(RDJ), which matches his elite pitch variance. The actual deficit stands and
is now precisely named: **one unvarying rate, zero pauses = zero contrast.**
He does not need to be slower; he needs to be *variable* — one deliberate
half-speed sentence per take (drill S3). The 110–150 zone still applies to
prepared remarks (toasts, stories, speeches).

### 4. Minimizers on heavy content
He shrink-wraps other people's serious disclosures with small words.
- "a little bit of family history" — for a family business collapsing
- "a little bit more about this embarrassment"
- "that must have been a really **eye-opening** experience" — for a described
  moral collision

Related: he nominalizes feelings ("embarrassingly" → "this embarrassment"),
which turns a person into a case study.

### 5. Cold face on a warm line → merged into #0 (the late smile)
Kept for history: s1 @7.0–9.4s, s4-risk @7.03s, s4-layer3-1 @5.0–6.7s.
**Exception, and he got it right:** s4-layer3-2, flat face on her disclosure —
that was correct congruence. He can read the room down; he struggles to come
back up (s12: she laughed, he stayed at 0% smile with posture collapsing).

### 6. Stacked questions → sibling of #0b (the buried question)
Asks two questions back to back, so only the second gets answered
(s1-take1, s3). Same mechanism as burying: can't leave a question alone in
the air. Fewer questions, more silence.

### 7. The braid is one-sided — in either direction (named 2026-08-14)
Cold takes 1–2: all questions, zero self (liked-not-known ceiling). Take 3:
all self, no question that survives. He has both failure modes and toggles
between them take to take; what he has not yet produced in a cold approach is
the alternation — ask, disclose, ask (drill D3). Note his disclosure raw
material is strong (two brands + AI agents = built-in motive/contrast/lately).

### 8. Gesture 0.0% — three takes running (newly scored 2026-08-14)
`gesture_active_pct = 0.0` in all three cold-approach takes, with an
energy_body_mismatch flag in take 2 (vocal peaks over a dead body). Was
previously unscored; now a deficit under the Power Sphere doctrine. Stillness
is his strength *under pressure*; in storytelling/delivery it reads as
"reporting, not reliving." Drill B1.

### 9. Sentence-final certainty — DOWNGRADED from Resolved (2026-08-14)
100% final-drop through the mixer session and cold takes 1–2, then **0%** in
take 3, with trail-off at 33% — on the boldest line he has ever run. The
skill exists but does not yet survive risk: the more exposed the content, the
higher the ending floats. Watch specifically on self-referential lines
("My name is…", "I own…").

### 10. Giving his name — DOWNGRADED from Resolved (2026-08-14)
Took five takes to install mid-conversation last session; then zero
introductions in cold takes 1–2 (an introductions drill). Returned in take 3.
Not yet automatic on the approach beat.

---

## Resolved — hold the gain

### 1. Filler — fixed within one session; REGRESSION WATCH (2026-08-14)
`11.1 → 13.5 → 5.3 → 5.4 → 0.0 → 0.0 → 0.0 → 0.0` per minute, then seven more
clean takes — and a return at 7.5/min in cold-take5, the first *multi-beat
conversational* load of the new campaign. Placement is diagnostic: "um" as the
first syllable AFTER a 1.39s held lead-in (pause-then-filler — the hold spent
on nothing), and "you know" bridging into a warm line. Fine on short scripted
beats; leaks under improvised length. Watch, don't re-drill yet.

### 2. The pre-turn hold — a genuine strength
He takes real silence *before* speaking: 3.09s (s4-risk), 2.45s (s4-layer3-2),
with uprightness *rising* through the hold (0.87 → 0.95, and 0.99). This is the
composure signal the rubrics ask for and he does it naturally.

### 3. Sentence-final certainty → DOWNGRADED to Open #9 (2026-08-14)

### 4. Giving his name → DOWNGRADED to Open #10 (2026-08-14)

---

## Native assets — build on these

- **Pitch variance is elite.** Scores of 94, 100, 100, 100, 90, and a 100/100
  on a cold approach (08-14 take 2); range up to 67–358 Hz. Melody is his best
  instrument. Research note: this is exactly the asset the RDJ profile runs on
  — fast-but-varied is *available* to him in a way it isn't to most people;
  what's missing is the pause-and-contrast half of that profile.
- **Warmth is genuine and provably movable.** Duchenne 84–100% always; and
  when given the smile-timing drill he executed it on the very next take
  (smile led the first word by 0.04s, warmth 60 = personal best). The
  correction pathway works; it just decays under load.
- **Genuine warmth.** Duchenne proportion is 84–100% of all smiles — when he
  smiles it is never social, always real.
- **Wit under pressure.** "I'm up to no good," "let's take this back somewhere
  real," "I don't try to be good, I try to be real" — all improvised, all
  memorable. The raw material is there; the discipline around it is the work.
- **He takes correction and applies it inside one session.** Filler and padding
  both moved on the take immediately following the note.

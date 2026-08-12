# How to use your communications coach

## The loop

1. **Record** a session — speech rehearsal, a networking conversation, a
   YouTube take, whatever you're working on. Video is best (you get posture,
   smile, and gaze analysis); audio alone still gets the full vocal breakdown.

2. **Drop the file in `sessions/`** with a descriptive name:

   ```
   sessions/2026-08-14-wedding-toast-take2.mp4
   ```

3. **Tell Claude Code:**

   ```
   Coach me: sessions/2026-08-14-wedding-toast-take2.mp4, context: speech
   ```

   Contexts: `speech`, `small-talk`, `networking`, `dinner-party`, `youtube`.
   Each has its own rubric in `rubrics/` — the same long pause that scores UP
   in a speech scores DOWN in small talk, so the context matters.

4. **Read the report** in `reports/YYYY-MM-DD-<name>.md`. It always ends with
   **THE ONE THING** — a single, concrete, drillable instruction with your
   current number and a target number.

5. **Drill the one thing. Record the next take.** Scores are tracked per
   context so you can watch the trend.

## What happens under the hood

One command runs everything:

```
bash pipeline/run_all.sh sessions/<file> <context>
```

That writes an analysis packet to `analysis/<file-stem>/`:

| File | What it holds |
|---|---|
| `transcript.md` / `.json` | Word-level timestamped transcript |
| `vocal_metrics.json` | WPM, fillers, pause map (deliberate vs. anxious), pitch melody, trail-off, jitter/shimmer |
| `body_metrics.json` | Posture trend, smile % (with Duchenne proxy), gaze, sway, gestures |
| `timeline.json` | Everything merged per second + incongruence flags |

The coach reads the packet (never the raw media) and scores it against the
context rubric.

## Score history

Every report is logged to `reports/score_history.csv`. See your trend:

```
python3 analysis/score_history.py --trend
```

Or ask Claude Code: "show my score trend."

## Practicing without a live event

You don't have to wait for a real conversation to get scored. `scenarios/`
holds practice decks — situation cards with the autopilot version, the move,
lines to keep in the pocket, and the metric each one is judged on. Pick a card,
record 60–90 seconds of yourself running it, and put the take through the same
loop:

```
sessions/2026-08-14-s7-big-fish-take1.m4a   →   context: networking
```

Naming the file with the scenario number keeps that situation's trend readable
in `reports/` separately from your context-wide average.

## Tips for useful recordings

- 1–5 minutes is the sweet spot; the pipeline handles longer fine.
- Frame yourself from the hips or chest up if you want posture/gesture data.
- For conversation contexts, mono phone audio is fine — the pause map,
  melody, and transcript analysis carry the coaching.
- Name files with a date and the scenario; the git history of `reports/`
  becomes your longitudinal progress record.

## The dimension profile

Every report scores eight dimensions alongside the headline number —
confidence, warmth, body language, presence, verbal acuity, unexpectedness,
curiosity and attunement. Definitions and calibration live in
`rubrics/dimensions.md`. The headline score is the rubric-weighted verdict for
the context; the dimensions tell you *which channel* carried the take and which
one sank it.

```
python3 analysis/score_history.py --dimensions
```

That prints every take as a column, with min/max/average per dimension, and
flags three things: the **bottleneck** (weakest average), the **lowest ceiling**
(the channel you've never once been good at), and your **strongest**. Two takes
can score within 2 points of each other on the headline and have completely
inverted profiles — the headline hides that; this doesn't.

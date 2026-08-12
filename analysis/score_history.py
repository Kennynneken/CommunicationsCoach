#!/usr/bin/env python3
"""Track coaching scores per context over time.

Append a session:  score_history.py --add --date 2026-08-14 --context speech \
                       --score 58 --session wedding-toast-take2
Show the trend:    score_history.py --trend [--context speech]

Data lives in reports/score_history.csv (date,context,score,session).
"""
import argparse
import csv
import signal
import sys
from pathlib import Path

# Die quietly when piped into head/less rather than dumping a BrokenPipeError.
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):  # not POSIX, or not the main thread
    pass

CSV_PATH = Path(__file__).resolve().parent.parent / "reports" / "score_history.csv"
CONTEXTS = ["speech", "small-talk", "networking", "dinner-party", "youtube"]


def load():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add(date, context, score, session):
    rows = load()
    rows.append({"date": date, "context": context, "score": str(score), "session": session})
    rows.sort(key=lambda r: r["date"])
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "context", "score", "session"])
        w.writeheader()
        w.writerows(rows)
    print(f"logged: {date} {context} {score}/100 ({session}) -> {CSV_PATH}")


def trend(context=None):
    rows = load()
    if not rows:
        print("No scores logged yet.")
        return
    contexts = [context] if context else [c for c in CONTEXTS if any(r["context"] == c for r in rows)]
    for ctx in contexts:
        sub = [r for r in rows if r["context"] == ctx]
        if not sub:
            print(f"{ctx}: no sessions yet")
            continue
        scores = [int(r["score"]) for r in sub]
        arrow = ""
        if len(scores) >= 2:
            d = scores[-1] - scores[-2]
            arrow = f"  ({'+' if d >= 0 else ''}{d} vs. previous)"
        print(f"\n== {ctx} — latest {scores[-1]}/100{arrow}, best {max(scores)}, {len(scores)} session(s)")
        for r in sub:
            bar = "#" * (int(r["score"]) // 2)
            print(f"  {r['date']}  {int(r['score']):3d} |{bar:<50}| {r['session']}")


DIMS = [
    ("confidence", "Confidence"),
    ("warmth", "Warmth"),
    ("body", "Body language"),
    ("presence", "Presence"),
    ("verbal", "Verbal acuity"),
    ("unexpected", "Unexpectedness"),
    ("curiosity", "Curiosity"),
    ("attunement", "Attunement"),
]
DIM_CSV = CSV_PATH.parent / "dimension_history.csv"


def dimensions(context=None):
    """Print the per-dimension profile across sessions (see rubrics/dimensions.md)."""
    if not DIM_CSV.exists():
        print(f"No dimension history yet ({DIM_CSV} not found).")
        return
    with DIM_CSV.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if not context or r["context"] == context]
    if not rows:
        print("No dimension rows for that context.")
        return

    width = max(len(label) for _, label in DIMS)
    print(f"\n{'':<{width}}  " + " ".join(f"{i+1:>3}" for i in range(len(rows)))
          + "   min  max  avg  last   Δ")
    means = {}
    for key, label in DIMS:
        vals = [int(r[key]) for r in rows]
        means[label] = sum(vals) / len(vals)
        d = vals[-1] - vals[-2] if len(vals) >= 2 else 0
        cells = " ".join(f"{v:>3}" for v in vals)
        print(f"{label:<{width}}  {cells}   {min(vals):>3}  {max(vals):>3}"
              f"  {means[label]:>3.0f}  {vals[-1]:>3}  {d:>+4}")

    overall = [int(r["score"]) for r in rows]
    print(f"{'HEADLINE':<{width}}  " + " ".join(f"{v:>3}" for v in overall) +
          f"   {min(overall):>3}  {max(overall):>3}  {sum(overall)/len(overall):>3.0f}"
          f"  {overall[-1]:>3}  {overall[-1] - overall[-2] if len(overall) >= 2 else 0:>+4}")

    print("\nsessions:")
    for i, r in enumerate(rows, 1):
        print(f"  {i:>2}. {r['date']}  {r['session']}")

    # The weakest average is usually the real bottleneck; the lowest ceiling is
    # the channel he has never once been good at.
    ceilings = {label: max(int(r[k]) for r in rows) for k, label in DIMS}
    print(f"\nbottleneck     : {min(means, key=means.get)} (avg {min(means.values()):.0f})")
    print(f"lowest ceiling : {min(ceilings, key=ceilings.get)} (best ever {min(ceilings.values())})")
    print(f"strongest      : {max(means, key=means.get)} (avg {max(means.values()):.0f})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--add", action="store_true", help="log a session score")
    mode.add_argument("--trend", action="store_true", help="print per-context trend table")
    mode.add_argument("--dimensions", action="store_true",
                      help="print the eight-dimension profile across sessions")
    ap.add_argument("--date", help="YYYY-MM-DD (required with --add)")
    ap.add_argument("--context", choices=CONTEXTS)
    ap.add_argument("--score", type=int, help="1-100 (required with --add)")
    ap.add_argument("--session", help="session name/stem (required with --add)")
    args = ap.parse_args()

    if args.add:
        missing = [n for n in ("date", "context", "score", "session") if getattr(args, n) is None]
        if missing:
            ap.error(f"--add requires --{', --'.join(missing)}")
        if not 1 <= args.score <= 100:
            ap.error("--score must be 1-100")
        add(args.date, args.context, args.score, args.session)
    elif args.dimensions:
        dimensions(args.context)
    else:
        trend(args.context)
    return 0


if __name__ == "__main__":
    sys.exit(main())

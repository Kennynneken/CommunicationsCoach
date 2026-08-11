#!/usr/bin/env python3
"""Track coaching scores per context over time.

Append a session:  score_history.py --add --date 2026-08-14 --context speech \
                       --score 58 --session wedding-toast-take2
Show the trend:    score_history.py --trend [--context speech]

Data lives in reports/score_history.csv (date,context,score,session).
"""
import argparse
import csv
import sys
from pathlib import Path

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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--add", action="store_true", help="log a session score")
    mode.add_argument("--trend", action="store_true", help="print per-context trend table")
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
    else:
        trend(args.context)
    return 0


if __name__ == "__main__":
    sys.exit(main())

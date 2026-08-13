#!/usr/bin/env python3
"""Print the coaching digest for an analysis packet.

Everything the coach needs to start scoring, in one block: the transcript, the
headline vocal numbers (speaking rate, not wall clock), the pause map, the body
trajectory, and any incongruence flags. Reading the raw JSON files is still
available for detail, but the digest is what turns a take around fast.

Usage: digest.py --outdir analysis/<stem>
"""
import argparse
import json
import sys
from pathlib import Path


def load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    d = Path(args.outdir)

    v = load(d / "vocal_metrics.json")
    b = load(d / "body_metrics.json")
    tl = load(d / "timeline.json")
    ctx = (d / "context.txt").read_text().strip() if (d / "context.txt").exists() else "?"
    tmd = d / "transcript.md"

    print("=================== COACHING DIGEST ===================")
    print(f"context: {ctx}")
    if tmd.exists():
        print("\n-- transcript --")
        print(tmd.read_text(encoding="utf-8").strip())

    if v and "error" not in v:
        sil, p, pit, inten = v["silence"], v["pauses"], v["pitch"], v["intensity"]
        print("\n-- vocal --")
        print(f"  wpm_speaking   {v['wpm_speaking']}   <- COACH ON THIS "
              f"(wpm_overall {v['wpm_overall']} is wall-clock, deflated by silence)")
        print(f"  lead_in        {sil['lead_in_s']}s hold before first word "
              f"| talking {sil['talking_s']}s of {sil['speech_span_s']}s span")
        print(f"  filler         {v['filler']['per_min']}/min  {v['filler']['words'] or '{}'}")
        print(f"  pauses         {p['count']} total | {p['deliberate_count']} DELIBERATE "
              f"| {p['anxious_gap_count']} anxious | p90 {p['p90_dur']}s")
        for q in p["list"]:
            print(f"                 {q['start']}s {q['dur']}s "
                  f"{'sentence-end' if q['after_sentence_end'] else 'mid-clause'}"
                  f"{' BRIDGED-BY-FILLER' if q['bridged_by_filler'] else ''}")
        print(f"  pitch          variance {pit['variance_score_0to100']}/100 "
              f"| range {pit['range_hz']}Hz | final-drop {pit['sentence_final_drop_pct']}%")
        print(f"  intensity      trail-off {inten['trail_off_sentences_pct']}% "
              f"| mean {inten['mean_db']}dB")

    if b and b.get("has_video") is not False:
        po, f, g, m = b["posture"], b["face"], b["gaze"], b["movement"]
        print("\n-- body --")
        print(f"  uprightness    {po['uprightness_mean']} ({po['uprightness_trend']}, "
              f"start->end {po['start_vs_end_delta']:+})")
        print(f"  smile          {f['smile_pct']}% | Duchenne {f['duchenne_pct_of_smiles']}% of them")
        print(f"  gaze           {g['toward_camera_pct']}% to camera | stability "
              f"{g['stability_score_0to100']}")
        print(f"  movement       sway {m['sway_score_0to100']} | gesture "
              f"{m['gesture_active_pct']}% | head-vel {m['head_velocity_mean']}")
        # Where the face goes flat matters as much as the average.
        cold = [x["t"] for x in f.get("smile_ts", []) if x["v"] < 0.05]
        if cold:
            print(f"  flat-face at   {', '.join(f'{t}s' for t in cold[:14])}"
                  f"{' …' if len(cold) > 14 else ''}")

    if tl:
        flags = tl.get("incongruence_flags") or []
        print(f"\n-- incongruence -- {flags if flags else 'none'}")

    print("=======================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())

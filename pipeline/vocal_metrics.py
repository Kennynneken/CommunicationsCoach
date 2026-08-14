#!/usr/bin/env python3
"""Compute vocal delivery metrics from audio.wav + transcript.json.

Outputs vocal_metrics.json into --outdir per pipeline/SPECS.md:
WPM, fillers, pause map (deliberate vs. anxious), pitch (parselmouth),
intensity/trail-off, jitter/shimmer.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PAUSE_MIN = 0.5          # inter-word gap that counts as a pause (s)
DELIBERATE_MIN = 0.8     # deliberate pause minimum duration (s)
FILLER_BRIDGE_WINDOW = 0.3
SINGLE_FILLERS = {"um", "uh", "er", "ah", "like"}
MULTI_FILLERS = [("you", "know"), ("sort", "of"), ("kind", "of"), ("i", "mean")]

# "like" is a filler in "it was, like, huge" but a verb in "I really like that"
# and a preposition in "a room like this". These guards keep real usages out of
# the filler count — a false positive there fakes a regression in a metric
# tracked longitudinally.
LIKE_COMPARATIVE_PREV = {
    "is", "was", "are", "were", "be", "been", "am",
    "feels", "feel", "felt", "looks", "look", "looked",
    "seems", "seem", "seemed", "sounds", "sound", "sounded",
}
LIKE_VERB_PREV = {
    "i", "you", "we", "they", "he", "she", "who", "people",
    "would", "wouldn't", "d", "do", "don't", "does", "doesn't",
    "did", "didn't", "to", "ll", "will", "might", "may", "really",
}
# "an event like this", "a room like that", "like a jet engine" — prepositional.
LIKE_PREPOSITIONAL_NEXT = {
    "this", "that", "these", "those", "a", "an", "the",
    "mine", "yours", "ours", "theirs", "him", "her", "them", "us", "me", "it",
}
LIKE_SKIP_ADVERBS = {
    "really", "real", "actually", "totally", "genuinely", "honestly",
    "especially", "particularly", "also", "still", "always", "never",
    "definitely", "absolutely",
}


def norm(word: str) -> str:
    return re.sub(r"[^a-z']", "", word.lower())


def ends_sentence(word: str) -> bool:
    return bool(re.search(r"[.!?…]$", word.strip()))


def like_is_filler(normed, i):
    """True when the "like" at index i is discourse filler, not verb/comparative.

    Walks back over intensifying adverbs so "I really like" reads the same as
    "I like". Anything preceded by a subject pronoun, modal or "to" is the verb.
    """
    j = i - 1
    while j >= 0 and normed[j] in LIKE_SKIP_ADVERBS and normed[j] not in LIKE_VERB_PREV:
        j -= 1
    if j < 0:
        return True
    prev = normed[j]
    # Quotative "I was like" IS filler; comparative "it was like huge" is not.
    # The subject is what separates them.
    if prev in {"was", "were", "am", "are"} and j > 0 and normed[j - 1] in {
        "i", "he", "she", "they", "we", "you",
    }:
        return True
    if i + 1 < len(normed) and normed[i + 1] in LIKE_PREPOSITIONAL_NEXT:
        return False
    # "What was that like (for you)?" / "what's it like" — wh-predicate, not
    # filler: "like" preceded by a pronoun object with a wh-word earlier in
    # the clause.
    if prev in {"that", "it", "this", "he", "she", "they"} and any(
        w in {"what", "how"} for w in normed[max(0, i - 6):i]
    ):
        return False
    return prev not in LIKE_COMPARATIVE_PREV and prev not in LIKE_VERB_PREV


def find_fillers(words):
    """Return (indices set, {filler: count}, [timestamps])."""
    idx, counts, times = set(), {}, []
    normed = [norm(w["w"]) for w in words]

    def add(i, name):
        if i not in idx:
            idx.add(i)
            counts[name] = counts.get(name, 0) + 1
            times.append(words[i]["start"])

    for i, n in enumerate(normed):
        if n in SINGLE_FILLERS:
            if n == "like" and not like_is_filler(normed, i):
                continue
            add(i, n)
    for a, b in MULTI_FILLERS:
        for i in range(len(normed) - 1):
            if normed[i] == a and normed[i + 1] == b:
                add(i, f"{a} {b}")
                idx.add(i + 1)
    return idx, counts, times


def build_pauses(words, filler_idx):
    pauses = []
    for i in range(len(words) - 1):
        gap = words[i + 1]["start"] - words[i]["end"]
        if gap < PAUSE_MIN:
            continue
        after_sentence = ends_sentence(words[i]["w"])
        # Bridged by filler: the word ending the pause is a filler, or the word
        # entering it was a filler and the gap is short enough to read as one unit.
        bridged = ((i + 1) in filler_idx) or (
            i in filler_idx and gap <= PAUSE_MIN + FILLER_BRIDGE_WINDOW
        )
        pauses.append(
            {
                "start": round(words[i]["end"], 2),
                "dur": round(gap, 2),
                "after_sentence_end": after_sentence,
                "bridged_by_filler": bool(bridged),
            }
        )
    return pauses


def pitch_intensity(audio_path, words):
    import numpy as np
    import parselmouth

    snd = parselmouth.Sound(str(audio_path))
    pitch = snd.to_pitch_ac(pitch_floor=60, pitch_ceiling=400)
    freqs = pitch.selected_array["frequency"]
    voiced = freqs[freqs > 0]
    if voiced.size == 0:
        return None, None, None

    mean_hz, sd_hz = float(np.mean(voiced)), float(np.std(voiced))
    lo, hi = float(np.percentile(voiced, 5)), float(np.percentile(voiced, 95))
    # SD 10 Hz -> 20, SD 45 Hz -> 90, linear, clamped.
    variance_score = max(0.0, min(100.0, 20 + (sd_hz - 10) * 2))

    intensity = snd.to_intensity()

    def pitch_at(t):
        v = pitch.get_value_at_time(t)
        return v if v and v > 0 else None

    def intensity_at(t):
        try:
            v = intensity.get_value(t)
        except Exception:
            return None
        return v if v == v else None  # NaN check

    # Sentence-final behavior: compare last 0.4s of the sentence-ending word
    # against the sentence's overall mean.
    final_drops, trail_offs, sent_start = [], [], 0.0
    for w in words:
        if not ends_sentence(w["w"]):
            continue
        end = w["end"]
        pre = [pitch_at(t) for t in np.arange(sent_start, max(sent_start + 0.1, end - 0.4), 0.05)]
        fin = [pitch_at(t) for t in np.arange(max(sent_start, end - 0.4), end, 0.05)]
        pre, fin = [x for x in pre if x], [x for x in fin if x]
        if pre and fin:
            final_drops.append(np.mean(fin) < np.mean(pre))
        pre_i = [intensity_at(t) for t in np.arange(sent_start, max(sent_start + 0.1, end - 0.4), 0.05)]
        fin_i = [intensity_at(t) for t in np.arange(max(sent_start, end - 0.4), end, 0.05)]
        pre_i, fin_i = [x for x in pre_i if x], [x for x in fin_i if x]
        if pre_i and fin_i:
            trail_offs.append(np.mean(fin_i) < np.mean(pre_i) - 6.0)  # >6 dB fade
        sent_start = end

    pitch_block = {
        "mean_hz": round(mean_hz, 1),
        "sd_hz": round(sd_hz, 1),
        "range_hz": [round(lo), round(hi)],
        "variance_score_0to100": round(variance_score),
        "sentence_final_drop_pct": round(100 * sum(final_drops) / len(final_drops))
        if final_drops
        else None,
    }

    ivals = intensity.values[0]
    # Silence frames come back as NaN or huge negative dB — keep audible frames only.
    ivals = ivals[np.isfinite(ivals) & (ivals > 0)]
    intensity_block = {
        "mean_db": round(float(np.mean(ivals)), 1),
        "sd_db": round(float(np.std(ivals)), 1),
        "trail_off_sentences_pct": round(100 * sum(trail_offs) / len(trail_offs))
        if trail_offs
        else None,
    }

    point_process = parselmouth.praat.call(snd, "To PointProcess (periodic, cc)", 60, 400)
    try:
        jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        shimmer = parselmouth.praat.call(
            [snd, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6
        )
    except Exception:
        jitter = shimmer = float("nan")
    steadiness = {
        "jitter_local_pct": round(jitter * 100, 2) if jitter == jitter else None,
        "shimmer_local_pct": round(shimmer * 100, 2) if shimmer == shimmer else None,
    }
    return pitch_block, intensity_block, steadiness


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="path to audio.wav")
    ap.add_argument("--outdir", required=True, help="dir containing transcript.json; output goes here")
    args = ap.parse_args()

    audio, outdir = Path(args.input), Path(args.outdir)
    tpath = outdir / "transcript.json"
    if not audio.exists():
        print(f"ERROR: audio not found: {audio}", file=sys.stderr)
        return 1
    if not tpath.exists():
        print(f"ERROR: transcript.json not found in {outdir} — run transcribe.py first.", file=sys.stderr)
        return 1
    try:
        import numpy  # noqa: F401
        import parselmouth  # noqa: F401
    except ImportError as e:
        print(f"ERROR: missing dependency ({e}) — run setup.sh first.", file=sys.stderr)
        return 1

    transcript = json.loads(tpath.read_text(encoding="utf-8"))
    words = transcript["words"]
    duration = transcript["duration_s"] or 1.0
    minutes = duration / 60.0

    if not words:
        (outdir / "vocal_metrics.json").write_text(json.dumps({"error": "no speech detected"}, indent=2))
        print("WARNING: no words in transcript; wrote stub vocal_metrics.json")
        return 0

    # Speaking rate.
    # wpm_overall divides by wall-clock, so a long silence before the first word
    # (or after the last) deflates it — a take that opens with a 3s composure
    # beat can read 156 WPM while the words themselves are sprinting at 240.
    # wpm_speaking is the articulation rate: words per minute of actual talking,
    # with lead-in, lead-out, and every counted pause removed.
    wpm_overall = len(words) / minutes
    wpm_by_minute = []
    for m in range(int(duration // 60) + (1 if duration % 60 > 5 else 0)):
        lo, hi = m * 60, min((m + 1) * 60, duration)
        n = sum(1 for w in words if lo <= w["start"] < hi)
        span_min = max((hi - lo) / 60.0, 1e-6)
        wpm_by_minute.append(round(n / span_min, 1))

    filler_idx, filler_counts, filler_times = find_fillers(words)
    pauses = build_pauses(words, filler_idx)

    deliberate = [
        p for p in pauses
        if p["dur"] >= DELIBERATE_MIN and p["after_sentence_end"] and not p["bridged_by_filler"]
    ]
    anxious = [p for p in pauses if (not p["after_sentence_end"]) or p["bridged_by_filler"]]

    durs = [p["dur"] for p in pauses]
    durs_sorted = sorted(durs)
    p90 = durs_sorted[max(0, int(round(0.9 * len(durs_sorted))) - 1)] if durs_sorted else 0.0

    # Silence at the edges of the take. The pause map only sees gaps *between*
    # words, so a held beat before speaking — the composure signal the rubrics
    # ask for — was previously invisible in the packet.
    lead_in = round(words[0]["start"], 2)
    lead_out = round(max(0.0, duration - words[-1]["end"]), 2)
    speech_span = max(words[-1]["end"] - words[0]["start"], 1e-6)
    talking_s = max(speech_span - sum(p["dur"] for p in pauses), 1e-6)
    wpm_speaking = len(words) / (talking_s / 60.0)

    pitch_block, intensity_block, steadiness = pitch_intensity(audio, words)

    metrics = {
        "wpm_overall": round(wpm_overall, 1),
        "wpm_speaking": round(wpm_speaking, 1),
        "wpm_by_minute": wpm_by_minute,
        "silence": {
            "lead_in_s": lead_in,
            "lead_out_s": lead_out,
            "speech_span_s": round(speech_span, 2),
            "talking_s": round(talking_s, 2),
        },
        "filler": {
            "count": sum(filler_counts.values()),
            "per_min": round(sum(filler_counts.values()) / minutes, 1),
            "words": dict(sorted(filler_counts.items(), key=lambda kv: -kv[1])),
            "timestamps": [round(t, 1) for t in sorted(filler_times)],
        },
        "pauses": {
            "count": len(pauses),
            "list": pauses,
            "mean_dur": round(sum(durs) / len(durs), 2) if durs else 0.0,
            "p90_dur": round(p90, 2),
            "deliberate_count": len(deliberate),
            "anxious_gap_count": len(anxious),
        },
        "pitch": pitch_block,
        "intensity": intensity_block,
        "steadiness": steadiness,
    }
    (outdir / "vocal_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(
        f"vocal metrics -> {outdir}/vocal_metrics.json "
        f"(wpm {metrics['wpm_overall']} overall / {metrics['wpm_speaking']} speaking, "
        f"lead-in {lead_in}s, fillers/min {metrics['filler']['per_min']}, "
        f"pauses {len(pauses)}: {len(deliberate)} deliberate / {len(anxious)} anxious)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

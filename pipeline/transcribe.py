#!/usr/bin/env python3
"""Transcribe audio with faster-whisper (model `small`, word timestamps, VAD).

Outputs into --outdir:
  transcript.json — {language, duration_s, words: [{w, start, end, p}], segments}
  transcript.md   — timestamped readable transcript, one segment per line.
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="path to audio.wav")
    ap.add_argument("--outdir", required=True, help="analysis output directory")
    ap.add_argument("--model", default="small", help="faster-whisper model size")
    args = ap.parse_args()

    audio = Path(args.input)
    if not audio.exists():
        print(f"ERROR: audio file not found: {audio}", file=sys.stderr)
        return 1
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: faster-whisper not installed — run setup.sh first.", file=sys.stderr)
        return 1

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments_iter, info = model.transcribe(
        str(audio), word_timestamps=True, vad_filter=True
    )

    words, segments = [], []
    for seg in segments_iter:
        segments.append(
            {"text": seg.text.strip(), "start": round(seg.start, 2), "end": round(seg.end, 2)}
        )
        for w in seg.words or []:
            words.append(
                {
                    "w": w.word.strip(),
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                    "p": round(w.probability, 2),
                }
            )

    transcript = {
        "language": info.language,
        "duration_s": round(info.duration, 2),
        "words": words,
        "segments": segments,
    }
    (outdir / "transcript.json").write_text(
        json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    def ts(t: float) -> str:
        m, s = divmod(int(t), 60)
        return f"{m:02d}:{s:02d}"

    lines = [f"# Transcript ({info.language}, {transcript['duration_s']}s)", ""]
    lines += [f"[{ts(s['start'])}] {s['text']}" for s in segments]
    (outdir / "transcript.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"transcribed {len(words)} words, {len(segments)} segments -> {outdir}/transcript.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())

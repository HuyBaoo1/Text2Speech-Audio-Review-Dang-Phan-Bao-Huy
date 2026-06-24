"""Score Qwen ASR text exports in ``audio.wav|transcript`` format."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tts_data_pipeline.asr import compare_transcriptions
from tts_data_pipeline.pipeline import normalize_text, strip_ground_truth_annotations


FIELDNAMES = [
    "path", "source_file", "provider", "model", "duration", "pass_quality_gate",
    "reference", "hypothesis", "wer", "cer", "manual_accept", "manual_error_tags", "manual_notes",
]


def read_ground_truth(directory: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in directory.glob("*.txt"):
        raw = path.read_text(encoding="utf-8")
        if raw.strip():
            # Keep annotation-only rows for coverage, but leave their score
            # empty because stripping the annotation yields no reference text.
            result[f"{path.stem}.wav"] = normalize_text(strip_ground_truth_annotations(raw))
    return result


def read_export(path: Path) -> tuple[dict[str, str], int, int]:
    transcripts: dict[str, str] = {}
    invalid = 0
    duplicates = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "|" not in raw:
            invalid += 1
            continue
        source, hypothesis = raw.split("|", 1)
        source = Path(source).name
        if not source.lower().endswith(".wav"):
            invalid += 1
            continue
        if source in transcripts:
            duplicates += 1
        transcripts[source] = normalize_text(hypothesis)
    return transcripts, invalid, duplicates


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", delete=False, dir=path.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        handle.write(content)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-txt", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--ground-truth", default="data/ground_truth_studio")
    parser.add_argument("--audio-folder", default="audio_samples/studio")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-jsonl", required=True)
    args = parser.parse_args()

    references = read_ground_truth(ROOT / args.ground_truth)
    transcripts, invalid, duplicates = read_export(ROOT / args.input_txt)
    rows: list[dict[str, str]] = []
    for source, reference in references.items():
        hypothesis = transcripts.get(source, "")
        stats = compare_transcriptions(reference, hypothesis) if reference else None
        rows.append({
            "path": str(Path(args.audio_folder) / source),
            "source_file": source,
            "provider": "qwen",
            "model": args.model,
            "duration": "",
            "pass_quality_gate": "",
            "reference": reference,
            "hypothesis": hypothesis,
            "wer": f"{stats['wer']:.6f}" if stats else "",
            "cer": f"{stats['cer']:.6f}" if stats else "",
            "manual_accept": "",
            "manual_error_tags": "",
            "manual_notes": "",
        })

    output_csv = ROOT / args.output_csv
    with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", delete=False, dir=output_csv.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, output_csv)

    output_jsonl = ROOT / args.output_jsonl
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=output_jsonl.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(temporary, output_jsonl)

    wers = [float(row["wer"]) for row in rows if row["wer"]]
    cers = [float(row["cer"]) for row in rows if row["cer"]]
    print(f"coverage={len(rows)}/{len(references)}; scoreable={len(wers)}")
    print(f"wer_avg={sum(wers) / len(wers):.4f}")
    print(f"cer_avg={sum(cers) / len(cers):.4f}")
    print(f"invalid_lines={invalid}; duplicate_lines={duplicates}; extra_outputs={len(set(transcripts) - set(references))}")


if __name__ == "__main__":
    main()

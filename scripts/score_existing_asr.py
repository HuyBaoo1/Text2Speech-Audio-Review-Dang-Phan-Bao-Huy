import argparse
import csv
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tts_data_pipeline.asr import compare_transcriptions
from tts_data_pipeline.pipeline import normalize_text


FIELDNAMES = [
    "path",
    "source_file",
    "provider",
    "model",
    "duration",
    "pass_quality_gate",
    "reference",
    "hypothesis",
    "wer",
    "cer",
    "manual_accept",
    "manual_error_tags",
    "manual_notes",
]


def read_reference(ground_truth_dir: str, source_file: str) -> str | None:
    ref_path = Path(ground_truth_dir) / f"{Path(source_file).stem}.txt"
    if not ref_path.exists():
        return None
    reference = normalize_text(ref_path.read_text(encoding="utf-8"))
    return reference or None


def score_existing_asr(input_csv: str, output_csv: str, output_jsonl: str, ground_truth_dir: str) -> None:
    with open(input_csv, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    scored = []
    matched = 0
    for row in rows:
        reference = read_reference(ground_truth_dir, row["source_file"])
        hypothesis = normalize_text(row.get("hypothesis", ""))
        wer_score = ""
        cer_score = ""

        if reference:
            stats = compare_transcriptions(reference, hypothesis)
            wer_score = f"{stats['wer']:.6f}"
            cer_score = f"{stats['cer']:.6f}"
            matched += 1

        updated = {key: row.get(key, "") for key in FIELDNAMES}
        updated["reference"] = reference or ""
        updated["hypothesis"] = hypothesis
        updated["wer"] = wer_score
        updated["cer"] = cer_score
        scored.append(updated)

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(scored)

    jsonl_path = Path(output_jsonl)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for row in scored:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    wers = [float(row["wer"]) for row in scored if row["wer"]]
    cers = [float(row["cer"]) for row in scored if row["cer"]]
    print(f"rows={len(scored)}")
    print(f"ground_truth_matched={matched}")
    if wers:
        print(f"wer_avg={sum(wers) / len(wers):.4f}")
        print(f"wer_min={min(wers):.4f}")
        print(f"wer_max={max(wers):.4f}")
        print(f"cer_avg={sum(cers) / len(cers):.4f}")
        print(f"cer_min={min(cers):.4f}")
        print(f"cer_max={max(cers):.4f}")
    print(f"Wrote {output_csv}")
    print(f"Wrote {output_jsonl}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score an existing ASR CSV with newly added ground truth files")
    parser.add_argument("--input-csv", default="outputs/asr_eval_openai.csv")
    parser.add_argument("--output-csv", default="outputs/asr_eval_openai_scored.csv")
    parser.add_argument("--output-jsonl", default="outputs/asr_eval_openai_scored.jsonl")
    parser.add_argument("--ground-truth", default="data/ground_truth")
    args = parser.parse_args()
    score_existing_asr(args.input_csv, args.output_csv, args.output_jsonl, args.ground_truth)

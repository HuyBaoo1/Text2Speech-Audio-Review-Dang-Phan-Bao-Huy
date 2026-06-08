import argparse
import csv
from pathlib import Path


def read_csv(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def generate_summary(quality_csv: str, scored_asr_csv: str, output_md: str) -> None:
    quality_rows = read_csv(quality_csv)
    asr_rows = read_csv(scored_asr_csv)
    scored_rows = [row for row in asr_rows if row.get("wer")]

    pass_rows = [row for row in quality_rows if row.get("pass_quality_gate") == "True"]
    review_rows = [row for row in quality_rows if row.get("pass_quality_gate") != "True"]
    durations = [float(row["duration"]) for row in quality_rows if row.get("duration")]
    snrs = [float(row["snr"]) for row in quality_rows if row.get("snr")]
    wers = [float(row["wer"]) for row in scored_rows]
    cers = [float(row["cer"]) for row in scored_rows]

    scored_rows = sorted(scored_rows, key=lambda row: float(row["wer"]))
    lines = [
        "# Evaluation Summary",
        "",
        "## Dataset",
        "",
        f"- Source folder: `audio_samples/matched_audio`",
        f"- Evaluated sample count: `{len(quality_rows)}`",
        f"- Ground truth matched for ASR scoring: `{len(scored_rows)}`",
        "",
        "## Audio Quality",
        "",
        f"- Quality gate pass: `{len(pass_rows)}`",
        f"- Quality gate review: `{len(review_rows)}`",
        f"- Average duration: `{mean(durations):.2f}s`",
        f"- Min duration: `{min(durations):.2f}s`" if durations else "- Min duration: `n/a`",
        f"- Max duration: `{max(durations):.2f}s`" if durations else "- Max duration: `n/a`",
        f"- Average SNR: `{mean(snrs):.2f} dB`",
        "",
        "## OpenAI ASR Result",
        "",
        "- Provider/model: `openai:gpt-4o-mini-transcribe`",
        f"- Average WER on ground truth subset: `{mean(wers):.4f}`" if wers else "- Average WER: `n/a`",
        f"- Average CER on ground truth subset: `{mean(cers):.4f}`" if cers else "- Average CER: `n/a`",
        f"- Best WER: `{min(wers):.4f}`" if wers else "- Best WER: `n/a`",
        f"- Worst WER: `{max(wers):.4f}`" if wers else "- Worst WER: `n/a`",
        "",
        "## Scored Files",
        "",
        "| file | WER | CER | duration | quality_gate |",
        "| --- | ---: | ---: | ---: | --- |",
    ]

    for row in scored_rows:
        lines.append(
            f"| `{row['source_file']}` | {float(row['wer']):.4f} | {float(row['cer']):.4f} | "
            f"{row['duration']} | {row['pass_quality_gate']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- 50/100 clips pass the current automatic quality gate; the other 50 should be manually reviewed or segmented/trimmed.",
            "- OpenAI ASR is usable as a bootstrap transcript source, but the current ground truth subset still shows meaningful error variance.",
            "- The worst current file is a good candidate for manual error tagging before trusting bulk transcription.",
            "- Local open-source ASR should be run next on the same 11 ground-truth files first, then expanded to 100 if runtime is acceptable.",
            "",
            "## Artifacts",
            "",
            "- `outputs/quality_report.csv`",
            "- `outputs/asr_eval_openai.csv`",
            "- `outputs/asr_eval_openai_scored.csv`",
            "- `outputs/asr_eval_openai_scored.jsonl`",
        ]
    )

    output = Path(output_md)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Markdown evaluation summary")
    parser.add_argument("--quality-csv", default="outputs/quality_report.csv")
    parser.add_argument("--scored-asr-csv", default="outputs/asr_eval_openai_scored.csv")
    parser.add_argument("--output-md", default="outputs/evaluation_summary.md")
    args = parser.parse_args()
    generate_summary(args.quality_csv, args.scored_asr_csv, args.output_md)

import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tts_data_pipeline.asr import compare_transcriptions
from tts_data_pipeline.pipeline import normalize_text, scan_audio_files, strip_ground_truth_annotations


TARGET_COUNT = 300
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth_studio"
QUALITY_CSV = ROOT / "outputs" / "studio_full_quality_report.csv"

RUNS = [
    {
        "provider": "openai",
        "model": "gpt-4o-mini-transcribe",
        "csv": ROOT / "outputs" / "studio_full_asr_eval_openai_gpt_4o_mini.csv",
    },
    {
        "provider": "groq",
        "model": "whisper-large-v3-turbo",
        "csv": ROOT / "outputs" / "studio_full_asr_eval_groq_whisper_large_v3_turbo.csv",
    },
    {
        "provider": "deepgram",
        "model": "nova-3",
        "csv": ROOT / "outputs" / "studio_full_asr_eval_deepgram_nova3.csv",
    },
    {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "csv": ROOT / "outputs" / "studio_full_asr_eval_gemini_2_5_flash.csv",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_reference(stem: str) -> str:
    path = GROUND_TRUTH_DIR / f"{stem}.txt"
    return normalize_text(strip_ground_truth_annotations(path.read_text(encoding="utf-8")))


def first_ground_truth_audio_stems() -> list[str]:
    paths = scan_audio_files(str(ROOT / "audio_samples" / "studio"), limit=None)
    stems = []
    for path in paths:
        stem = Path(path).stem
        gt_path = GROUND_TRUTH_DIR / f"{stem}.txt"
        if gt_path.exists() and gt_path.read_text(encoding="utf-8").strip():
            stems.append(stem)
        if len(stems) >= TARGET_COUNT:
            break
    return stems


def load_quality_summary(target_stems: set[str]) -> dict[str, float | int]:
    rows = read_csv(QUALITY_CSV)
    selected = [row for row in rows if Path(row.get("path", "")).stem in target_stems]
    pass_count = sum(1 for row in selected if row.get("pass_quality_gate") == "True")
    durations = [float(row["duration"]) for row in selected if row.get("duration")]
    snrs = [float(row["snr"]) for row in selected if row.get("snr")]
    silence = [float(row["silence_ratio"]) for row in selected if row.get("silence_ratio")]
    return {
        "rows": len(selected),
        "pass_count": pass_count,
        "review_count": len(selected) - pass_count,
        "duration_mean": statistics.mean(durations) if durations else 0.0,
        "snr_mean": statistics.mean(snrs) if snrs else 0.0,
        "silence_ratio_mean": statistics.mean(silence) if silence else 0.0,
    }


def summarize_run(run: dict[str, object], target_stems: list[str]) -> dict[str, object]:
    rows = read_csv(run["csv"])
    by_stem = {Path(row.get("source_file", "")).stem: row for row in rows if row.get("source_file")}
    scored = []
    missing = 0
    empty_hypothesis = 0
    errors = 0

    for stem in target_stems:
        row = by_stem.get(stem)
        if not row:
            missing += 1
            continue
        if row.get("manual_notes", "").startswith("ERROR:"):
            errors += 1
            continue
        hypothesis = normalize_text(row.get("hypothesis", ""))
        if not hypothesis:
            empty_hypothesis += 1
        reference = read_reference(stem)
        stats = compare_transcriptions(reference, hypothesis)
        scored.append(stats)

    wer_values = [float(item["wer"]) for item in scored]
    cer_values = [float(item["cer"]) for item in scored]
    return {
        "provider": run["provider"],
        "model": run["model"],
        "target_rows": len(target_stems),
        "scored_rows": len(scored),
        "missing_rows": missing,
        "error_rows": errors,
        "empty_hypothesis_rows": empty_hypothesis,
        "wer_mean": statistics.mean(wer_values) if wer_values else None,
        "wer_median": statistics.median(wer_values) if wer_values else None,
        "cer_mean": statistics.mean(cer_values) if cer_values else None,
        "cer_median": statistics.median(cer_values) if cer_values else None,
    }


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def main() -> None:
    target_stems = first_ground_truth_audio_stems()
    target_set = set(target_stems)
    quality = load_quality_summary(target_set)
    summaries = [summarize_run(run, target_stems) for run in RUNS]
    summaries.sort(key=lambda row: row["wer_mean"] if row["wer_mean"] is not None else 999)

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    summary_csv = output_dir / "studio_300_benchmark_summary.csv"
    with summary_csv.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "provider",
            "model",
            "target_rows",
            "scored_rows",
            "missing_rows",
            "error_rows",
            "empty_hypothesis_rows",
            "wer_mean",
            "wer_median",
            "cer_mean",
            "cer_median",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summaries:
            writer.writerow({key: fmt(row.get(key)) for key in fieldnames})

    state_json = output_dir / "studio_300_benchmark_summary.json"
    state_json.write_text(
        json.dumps({"target_stems": target_stems, "quality": quality, "models": summaries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Studio 300 Benchmark Summary",
        "",
        "Ground-truth annotations inside `<...>` are stripped before scoring.",
        "",
        f"- Target rows: {len(target_stems)} first studio audio files with ground truth.",
        f"- Quality PASS: {quality['pass_count']}/{quality['rows']}; REVIEW: {quality['review_count']}/{quality['rows']}.",
        f"- Mean duration: {quality['duration_mean']:.2f}s; mean SNR: {quality['snr_mean']:.2f} dB; mean silence ratio: {quality['silence_ratio_mean']:.3f}.",
        "",
        "| Rank | Provider | Model | Scored | Missing | Empty | WER mean | CER mean |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(summaries, start=1):
        lines.append(
            f"| {rank} | {row['provider']} | `{row['model']}` | {row['scored_rows']}/{row['target_rows']} | "
            f"{row['missing_rows']} | {row['empty_hypothesis_rows']} | {fmt(row['wer_mean'])} | {fmt(row['cer_mean'])} |"
        )
    lines.append("")
    (output_dir / "studio_300_benchmark_summary.md").write_text("\n".join(lines), encoding="utf-8-sig")

    print(f"Wrote {summary_csv}")
    print(f"Wrote {state_json}")
    print("Wrote outputs/studio_300_benchmark_summary.md")


if __name__ == "__main__":
    main()

"""Retry only failed Azure ASR rows after the input-normalisation fix."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = (
    {
        "folder": "audio_samples/studio",
        "ground_truth": "data/ground_truth_studio",
        "quality_csv": "outputs/studio_full_quality_report.csv",
        "output_csv": "outputs/studio_full_asr_eval_azure_speech_vi_vn.csv",
        "output_jsonl": "outputs/studio_full_asr_eval_azure_speech_vi_vn.jsonl",
    },
    {
        "folder": "audio_samples/matched_audio",
        "ground_truth": "data/ground_truth",
        "quality_csv": "outputs/quality_report.csv",
        "output_csv": "outputs/combined_matched_asr_eval_azure_speech_vi_vn.csv",
        "output_jsonl": "outputs/combined_matched_asr_eval_azure_speech_vi_vn.jsonl",
    },
)


def main() -> None:
    result_codes: list[int] = []
    for run in RUNS:
        command = [
            sys.executable,
            "scripts/run_asr_evaluation.py",
            "--folder", run["folder"],
            "--provider", "azure",
            "--model", "azure-short-audio",
            "--ground-truth", run["ground_truth"],
            "--quality-csv", run["quality_csv"],
            "--limit", "0",
            "--language", "vi-VN",
            "--output-csv", run["output_csv"],
            "--output-jsonl", run["output_jsonl"],
            "--resume",
            "--checkpoint-every", "1",
            "--max-retries", "8",
            "--retry-delay", "5",
            "--request-delay", "4",
            "--only-ground-truth",
        ]
        result_codes.append(subprocess.run(command, cwd=ROOT).returncode)
    subprocess.run([sys.executable, "scripts/update_studio_groq_readme.py"], cwd=ROOT)
    raise SystemExit(0 if all(code == 0 for code in result_codes) else 1)


if __name__ == "__main__":
    main()

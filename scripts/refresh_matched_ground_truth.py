"""Transcribe only newly grounded matched_audio files, preserving CSV checkpoints.

Each model resumes from its existing output CSV.  `run_asr_evaluation.py` writes an
atomic checkpoint after every file, so this runner is safe to restart after a
timeout or a provider-side rate limit.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMON = [
    "--folder", "audio_samples/matched_audio",
    "--ground-truth", "data/ground_truth",
    "--quality-csv", "outputs/quality_report.csv",
    "--limit", "0",
    "--resume",
    "--checkpoint-every", "1",
    "--max-retries", "5",
    "--retry-delay", "3",
    "--only-ground-truth",
]

# Azure is intentionally omitted: retry_azure_checkpoints.py is already running
# its own resumable studio -> matched_audio sequence against the same CSV.
RUNS = {
    "elevenlabs": [
        ("elevenlabs", "scribe_v2", "vie", "outputs/combined_matched_asr_eval_elevenlabs_scribe_v2.csv", "outputs/combined_matched_asr_eval_elevenlabs_scribe_v2.jsonl", "0"),
    ],
    "deepgram": [
        ("deepgram", "nova-3", "vi", "outputs/combined_matched_asr_eval_deepgram_nova3.csv", "outputs/combined_matched_asr_eval_deepgram_nova3.jsonl", "0"),
    ],
    "groq": [
        ("groq", "whisper-large-v3", "vi", "outputs/matched_openai_parallel_asr_eval_whisper_large_v3.csv", "outputs/matched_openai_parallel_asr_eval_whisper_large_v3.jsonl", "3.5"),
        ("groq", "whisper-large-v3-turbo", "vi", "outputs/matched_openai_parallel_asr_eval_whisper_large_v3_turbo.csv", "outputs/matched_openai_parallel_asr_eval_whisper_large_v3_turbo.jsonl", "3.5"),
    ],
    "gemini": [
        ("gemini", "gemini-3.5-flash", "Vietnamese", "outputs/matched_asr_eval_gemini_3_5_flash.csv", "outputs/matched_asr_eval_gemini_3_5_flash.jsonl", "0"),
        ("gemini", "gemini-3.1-flash-lite", "Vietnamese", "outputs/matched_asr_eval_gemini_3_1_flash_lite.csv", "outputs/matched_asr_eval_gemini_3_1_flash_lite.jsonl", "0"),
        ("gemini", "gemini-2.5-flash", "Vietnamese", "outputs/matched_asr_eval_gemini_2_5_flash.csv", "outputs/matched_asr_eval_gemini_2_5_flash.jsonl", "0"),
        ("gemini", "gemini-2.5-pro", "Vietnamese", "outputs/matched_asr_eval_gemini_2_5_pro.csv", "outputs/matched_asr_eval_gemini_2_5_pro.jsonl", "0"),
    ],
    "openai": [
        ("openai", "gpt-4o-mini-transcribe", "vi", "outputs/asr_eval_openai.csv", "outputs/asr_eval_openai.jsonl", "0"),
        ("openai", "gpt-4o-transcribe", "vi", "outputs/matched_openai_parallel_asr_eval_gpt_4o_transcribe.csv", "outputs/matched_openai_parallel_asr_eval_gpt_4o_transcribe.jsonl", "0"),
        ("openai-realtime", "gpt-realtime-2", "vi", "outputs/matched_openai_parallel_asr_eval_gpt_realtime_2.csv", "outputs/matched_openai_parallel_asr_eval_gpt_realtime_2.jsonl", "0"),
    ],
}


def run(group: str) -> int:
    result = 0
    for provider, model, language, output_csv, output_jsonl, request_delay in RUNS[group]:
        command = [
            sys.executable,
            "scripts/run_asr_evaluation.py",
            *COMMON,
            "--provider", provider,
            "--model", model,
            "--language", language,
            "--output-csv", output_csv,
            "--output-jsonl", output_jsonl,
            "--request-delay", request_delay,
        ]
        print(f"\n=== {provider}:{model} ===", flush=True)
        result = max(result, subprocess.run(command, cwd=ROOT).returncode)

    # The mini-transcribe raw CSV predates on-the-fly scoring; refresh its scored
    # counterpart after adding the four new rows.
    if group == "openai":
        score = [
            sys.executable,
            "scripts/score_existing_asr.py",
            "--input-csv", "outputs/asr_eval_openai.csv",
            "--output-csv", "outputs/combined_matched_asr_eval_openai_gpt_4o_mini_scored.csv",
            "--output-jsonl", "outputs/combined_matched_asr_eval_openai_gpt_4o_mini_scored.jsonl",
            "--ground-truth", "data/ground_truth",
        ]
        result = max(result, subprocess.run(score, cwd=ROOT).returncode)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("group", choices=tuple(RUNS))
    args = parser.parse_args()
    raise SystemExit(run(args.group))


if __name__ == "__main__":
    main()

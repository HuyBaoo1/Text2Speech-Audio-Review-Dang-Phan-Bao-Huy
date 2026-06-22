"""Update the existing README benchmark table from Studio + matched_audio checkpoints."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
TOTAL_TARGET = 2546 + 31


class Candidate(TypedDict):
    label: str
    studio: str
    matched: str


CANDIDATES: list[Candidate] = [
    {"label": "ElevenLabs `scribe_v2`", "studio": "studio_full_asr_eval_elevenlabs_scribe_v2.csv", "matched": "combined_matched_asr_eval_elevenlabs_scribe_v2.csv"},
    {"label": "Gemini `gemini-3.5-flash`", "studio": "studio_full_asr_eval_gemini_3_5_flash.csv", "matched": "matched_asr_eval_gemini_3_5_flash.csv"},
    {"label": "Gemini `gemini-3.1-flash-lite`", "studio": "studio_full_asr_eval_gemini_3_1_flash_lite.csv", "matched": "matched_asr_eval_gemini_3_1_flash_lite.csv"},
    {"label": "OpenAI `gpt-4o-mini-transcribe`", "studio": "studio_full_asr_eval_openai_gpt_4o_mini.csv", "matched": "combined_matched_asr_eval_openai_gpt_4o_mini_scored.csv"},
    {"label": "Groq `whisper-large-v3`", "studio": "openai_parallel_asr_eval_whisper_large_v3.csv", "matched": "matched_openai_parallel_asr_eval_whisper_large_v3.csv"},
    {"label": "Groq `whisper-large-v3-turbo`", "studio": "studio_full_asr_eval_groq_whisper_large_v3_turbo.csv", "matched": "matched_openai_parallel_asr_eval_whisper_large_v3_turbo.csv"},
    {"label": "Deepgram `nova-3`", "studio": "studio_full_asr_eval_deepgram_nova3.csv", "matched": "combined_matched_asr_eval_deepgram_nova3.csv"},
    {"label": "Gemini `gemini-2.5-flash`", "studio": "studio_full_asr_eval_gemini_2_5_flash.csv", "matched": "matched_asr_eval_gemini_2_5_flash.csv"},
    {"label": "Azure `azure-short-audio`", "studio": "studio_full_asr_eval_azure_speech_vi_vn.csv", "matched": "combined_matched_asr_eval_azure_speech_vi_vn.csv"},
    {"label": "Gemini `gemini-2.5-pro`", "studio": "studio_full_asr_eval_gemini_2_5_pro.csv", "matched": "matched_asr_eval_gemini_2_5_pro.csv"},
]


def load_csv(filename: str, ground_truth_dir: str) -> list[dict[str, str]]:
    path = ROOT / "outputs" / filename
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    stems = {item.stem for item in (ROOT / ground_truth_dir).glob("*.txt") if item.read_text(encoding="utf-8").strip()}
    return [row for row in rows if Path(row.get("source_file", "")).stem in stems]


def summarize(candidate: Candidate) -> dict[str, object]:
    all_rows = load_csv(candidate["studio"], "data/ground_truth_studio") + load_csv(
        candidate["matched"], "data/ground_truth"
    )
    errors = [row for row in all_rows if row.get("manual_notes", "").startswith("ERROR:")]
    completed = [row for row in all_rows if row.get("source_file") and row not in errors]
    scored = [row for row in completed if row.get("wer") and row.get("cer")]
    wer = sum(float(row["wer"]) for row in scored) / len(scored) if scored else None
    cer = sum(float(row["cer"]) for row in scored) / len(scored) if scored else None
    return {
        "label": candidate["label"],
        "completed": len(completed),
        "errors": len(errors),
        "empty": sum(not row.get("hypothesis", "").strip() for row in scored),
        "wer": wer,
        "cer": cer,
        "full": len(completed) == TOTAL_TARGET and not errors and wer is not None and cer is not None,
    }


def replace_main_table(rows: list[dict[str, object]]) -> str:
    content = README.read_text(encoding="utf-8")
    start_heading = "### Combined Ground-Truth Benchmark (Studio + matched_audio)"
    start = content.find(start_heading)
    if start < 0:
        start = content.index("### Studio Full")
    end = content.index("### ElevenLabs Detail", start)

    complete = sorted(
        (row for row in rows if row["full"]), key=lambda row: (float(row["wer"]), float(row["cer"]))
    )
    incomplete = sorted((row for row in rows if not row["full"]), key=lambda row: str(row["label"]))
    lines = [
        start_heading,
        "",
        "WER/CER là trung bình theo từng audio có ground truth của cả Studio (2546) và matched_audio (31).",
        "",
        "| Rank | Model | Coverage | WER | CER | Kết luận |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for rank, row in enumerate(complete, start=1):
        conclusion = "Best complete cross-dataset result" if rank == 1 else "Complete cross-dataset result"
        if row["empty"]:
            conclusion += f"; {row['empty']} empty output"
        lines.append(
            f"| {rank} | {row['label']} | {row['completed']}/{TOTAL_TARGET} | {float(row['wer']):.4f} | "
            f"{float(row['cer']):.4f} | {conclusion} |"
        )
    for row in incomplete:
        wer = "-" if row["wer"] is None else f"{float(row['wer']):.4f}"
        cer = "-" if row["cer"] is None else f"{float(row['cer']):.4f}"
        lines.append(
            f"| - | {row['label']} | {row['completed']}/{TOTAL_TARGET} | {wer} | {cer} | "
            f"Partial; excluded from rank ({row['errors']} API errors) |"
        )
    if complete:
        lines.extend(
            [
                "",
                f"Kết luận ngắn: {complete[0]['label']} hiện có WER tốt nhất trong các model đã hoàn tất cả hai dataset.",
                "",
            ]
        )
    return content[:start] + "\n".join(lines) + content[end:]


def atomic_write(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        handle.write(content)
    os.replace(temporary, path)


if __name__ == "__main__":
    atomic_write(README, replace_main_table([summarize(candidate) for candidate in CANDIDATES]))
    print("Updated README combined all-model benchmark summary.")

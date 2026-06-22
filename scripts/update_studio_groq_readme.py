"""Render separate noisy matched_audio and clean studio benchmark tables."""

from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import TypedDict


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


class Candidate(TypedDict):
    label: str
    studio: str
    matched: str


# These are the models that have benchmark checkpoints for both datasets.  A
# model with a partial Studio run is retained and explicitly excluded from rank.
CANDIDATES: list[Candidate] = [
    {"label": "ElevenLabs `scribe_v2`", "studio": "studio_full_asr_eval_elevenlabs_scribe_v2.csv", "matched": "combined_matched_asr_eval_elevenlabs_scribe_v2.csv"},
    {"label": "Gemini `gemini-3.5-flash`", "studio": "studio_full_asr_eval_gemini_3_5_flash.csv", "matched": "matched_asr_eval_gemini_3_5_flash.csv"},
    {"label": "Gemini `gemini-3.1-flash-lite`", "studio": "studio_full_asr_eval_gemini_3_1_flash_lite.csv", "matched": "matched_asr_eval_gemini_3_1_flash_lite.csv"},
    {"label": "Gemini `gemini-2.5-flash`", "studio": "studio_full_asr_eval_gemini_2_5_flash.csv", "matched": "matched_asr_eval_gemini_2_5_flash.csv"},
    {"label": "Gemini `gemini-2.5-pro`", "studio": "studio_full_asr_eval_gemini_2_5_pro.csv", "matched": "matched_asr_eval_gemini_2_5_pro.csv"},
    {"label": "OpenAI `gpt-4o-mini-transcribe`", "studio": "studio_full_asr_eval_openai_gpt_4o_mini.csv", "matched": "combined_matched_asr_eval_openai_gpt_4o_mini_scored.csv"},
    {"label": "OpenAI `gpt-4o-transcribe`", "studio": "openai_parallel_asr_eval_gpt_4o_transcribe.csv", "matched": "matched_openai_parallel_asr_eval_gpt_4o_transcribe.csv"},
    {"label": "OpenAI `gpt-realtime-2`", "studio": "openai_parallel_asr_eval_gpt_realtime_2.csv", "matched": "matched_openai_parallel_asr_eval_gpt_realtime_2.csv"},
    {"label": "Groq `whisper-large-v3`", "studio": "openai_parallel_asr_eval_whisper_large_v3.csv", "matched": "matched_openai_parallel_asr_eval_whisper_large_v3.csv"},
    {"label": "Groq `whisper-large-v3-turbo`", "studio": "studio_full_asr_eval_groq_whisper_large_v3_turbo.csv", "matched": "matched_openai_parallel_asr_eval_whisper_large_v3_turbo.csv"},
    {"label": "Deepgram `nova-3`", "studio": "studio_full_asr_eval_deepgram_nova3.csv", "matched": "combined_matched_asr_eval_deepgram_nova3.csv"},
    {"label": "Azure `azure-short-audio`", "studio": "studio_full_asr_eval_azure_speech_vi_vn.csv", "matched": "combined_matched_asr_eval_azure_speech_vi_vn.csv"},
]


def ground_truth_stems(directory: str) -> set[str]:
    return {
        item.stem
        for item in (ROOT / directory).glob("*.txt")
        if item.read_text(encoding="utf-8").strip()
    }


def is_error(row: dict[str, str]) -> bool:
    return row.get("manual_notes", "").startswith("ERROR:")


def prefer_row(current: dict[str, str] | None, candidate: dict[str, str]) -> dict[str, str]:
    if current is None or (is_error(current) and not is_error(candidate)):
        return candidate
    return current


def scoped_rows(filename: str, stems: set[str]) -> list[dict[str, str]]:
    path = ROOT / "outputs" / filename
    if not path.exists():
        return []
    selected: dict[str, dict[str, str]] = {}
    with open(path, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            source = row.get("source_file", "")
            if Path(source).stem not in stems:
                continue
            selected[source] = prefer_row(selected.get(source), row)
    return list(selected.values())


def summarize(candidate: Candidate, dataset: str, stems: set[str]) -> dict[str, object]:
    filename = candidate[dataset]  # type: ignore[literal-required]
    rows = scoped_rows(filename, stems)
    errors = [row for row in rows if is_error(row)]
    completed = [row for row in rows if not is_error(row)]
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
        # A small number of ground-truth rows are annotation-only and therefore
        # deliberately have no WER/CER. Coverage is still complete when every
        # target has a non-error response and the model has scored rows.
        "full": len(completed) == len(stems) and not errors and wer is not None and cer is not None,
    }


def table(dataset: str, title: str, description: str, stems: set[str]) -> str:
    results = [summarize(candidate, dataset, stems) for candidate in CANDIDATES]
    complete = sorted((row for row in results if row["full"]), key=lambda row: (float(row["wer"]), float(row["cer"])))
    partial = sorted((row for row in results if not row["full"]), key=lambda row: str(row["label"]))
    target = len(stems)
    lines = [
        f"### {title}",
        "",
        description,
        "",
        "| Rank | Model | Coverage | WER | CER | Kết luận |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for rank, row in enumerate(complete, start=1):
        note = "Tốt nhất trên tập này" if rank == 1 else "Đủ coverage, có thể so sánh trực tiếp"
        if row["empty"]:
            note += f"; {row['empty']} output rỗng"
        lines.append(
            f"| {rank} | {row['label']} | {row['completed']}/{target} | {float(row['wer']):.4f} | "
            f"{float(row['cer']):.4f} | {note} |"
        )
    for row in partial:
        wer = "-" if row["wer"] is None else f"{float(row['wer']):.4f}"
        cer = "-" if row["cer"] is None else f"{float(row['cer']):.4f}"
        missing = target - int(row["completed"])
        detail = f"Partial; thiếu {missing} mẫu"
        if row["errors"]:
            detail += f", {row['errors']} API errors"
        lines.append(f"| - | {row['label']} | {row['completed']}/{target} | {wer} | {cer} | {detail} |")
    if complete:
        lines.extend(["", f"Kết luận ngắn: {complete[0]['label']} có WER thấp nhất trong các model hoàn tất trên tập này.", ""])
    return "\n".join(lines)


def update_readme(content: str) -> str:
    readme = README.read_text(encoding="utf-8")
    benchmark = readme.index("## Benchmark Summary")
    start = readme.find("\n", benchmark) + 1
    while start < len(readme) and readme[start] == "\n":
        start += 1
    end = readme.index("### ElevenLabs Detail", start)
    return readme[:start] + content + "\n" + readme[end:]


def atomic_write(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        handle.write(content)
    os.replace(temporary, path)


if __name__ == "__main__":
    matched = ground_truth_stems("data/ground_truth")
    studio = ground_truth_stems("data/ground_truth_studio")
    content = "\n\n".join(
        [
            table("matched", "matched_audio Benchmark — noisy / tạp âm", "Dữ liệu internet/YouTube có noise và tạp âm; target hiện tại là 35 audio có ground truth.", matched),
            table("studio", "Studio Benchmark — clean", "Dữ liệu thu studio sạch; target hiện tại là 2546 audio có ground truth.", studio),
        ]
    )
    atomic_write(README, update_readme(content))
    print("Updated README with separate matched_audio and studio benchmark tables.")

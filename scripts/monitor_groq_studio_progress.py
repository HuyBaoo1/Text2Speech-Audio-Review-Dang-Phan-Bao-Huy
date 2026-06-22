"""Write Groq Studio benchmark progress every N minutes until both runs finish."""

from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = 2546
MODELS = (
    ("whisper-large-v3", "openai_parallel_asr_eval_whisper_large_v3.csv"),
    ("whisper-large-v3-turbo (historical Studio result)", "studio_full_asr_eval_groq_whisper_large_v3_turbo.csv"),
)


def status(model: str, filename: str) -> dict[str, object]:
    path = ROOT / "outputs" / filename
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors = [row for row in rows if row.get("manual_notes", "").startswith("ERROR:")]
    completed = [row for row in rows if row.get("source_file") and row not in errors]
    return {
        "model": model,
        "completed": len(completed),
        "errors": len(errors),
        "done": len(completed) == TARGET and not errors,
    }


def append_snapshot(path: Path, rows: list[dict[str, object]], completed: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(
            "# Groq Studio Benchmark Progress\n\n| Timestamp | Model | Coverage | Errors | Status |\n| --- | --- | ---: | ---: | --- |\n",
            encoding="utf-8",
        )
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as handle:
        for row in rows:
            state = "complete" if row["done"] else "running"
            handle.write(
                f"| {timestamp} | `{row['model']}` | {row['completed']}/{TARGET} | {row['errors']} | {state} |\n"
            )
        if completed:
            handle.write(f"\nCompleted at {timestamp}. README benchmark summary can now be refreshed.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor Groq Studio benchmark progress")
    parser.add_argument("--interval-minutes", type=float, default=15)
    parser.add_argument("--output", default="outputs/groq_studio_progress.md")
    args = parser.parse_args()
    interval_seconds = max(args.interval_minutes, 1 / 60) * 60
    output = ROOT / args.output
    while True:
        rows = [status(model, filename) for model, filename in MODELS]
        complete = all(bool(row["done"]) for row in rows)
        append_snapshot(output, rows, complete)
        if complete:
            return
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()

"""Record progress for one resumable ASR CSV at a fixed interval."""

from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def snapshot(csv_path: Path, target: int) -> tuple[int, int, bool]:
    with open(csv_path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors = [row for row in rows if row.get("manual_notes", "").startswith("ERROR:")]
    completed = [row for row in rows if row.get("source_file") and row not in errors]
    return len(completed), len(errors), len(completed) == target and not errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Write ASR checkpoint progress every N minutes")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--target", type=int, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--interval-minutes", type=float, default=15)
    args = parser.parse_args()
    csv_path = ROOT / args.csv
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        output.write_text(
            "# ASR Benchmark Progress\n\n| Timestamp | Model | Coverage | Errors | Status |\n| --- | --- | ---: | ---: | --- |\n",
            encoding="utf-8",
        )
    while True:
        completed, errors, done = snapshot(csv_path, args.target)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        with open(output, "a", encoding="utf-8") as handle:
            status = "complete" if done else "running"
            handle.write(f"| {timestamp} | `{args.model}` | {completed}/{args.target} | {errors} | {status} |\n")
        if done:
            return
        time.sleep(max(args.interval_minutes, 1 / 60) * 60)


if __name__ == "__main__":
    main()

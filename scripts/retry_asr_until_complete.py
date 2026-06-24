"""Repeat a resumable ASR run until every target row succeeds.

This is intended for transient provider quota/capacity failures.  Each round
delegates to ``run_asr_evaluation.py --resume``; successful rows are never
submitted again, while error rows are retried after a configurable cooldown.
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def count_rows(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    with open(path, encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors = sum(row.get("manual_notes", "").startswith("ERROR:") for row in rows)
    completed = sum(bool(row.get("source_file")) and not row.get("manual_notes", "").startswith("ERROR:") for row in rows)
    return completed, errors


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, suffix=".tmp") as handle:
        temporary = Path(handle.name)
        handle.write(content)
    os.replace(temporary, path)


def write_state(path: Path, *, round_number: int, completed: int, errors: int, target: int, status: str) -> None:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    atomic_write(
        path,
        "# ASR Retry Progress\n\n"
        "| Timestamp | Round | Coverage | Errors | Status |\n"
        "| --- | ---: | ---: | ---: | --- |\n"
        f"| {now} | {round_number} | {completed}/{target} | {errors} | {status} |\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--ground-truth", required=True)
    parser.add_argument("--quality-csv", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--target", type=int, required=True)
    parser.add_argument("--cooldown-seconds", type=int, default=900)
    parser.add_argument("--request-delay", type=float, default=2)
    parser.add_argument("--max-retries", type=int, default=8)
    parser.add_argument("--retry-delay", type=float, default=5)
    parser.add_argument("--wait-pid", type=int)
    parser.add_argument("--state-file", required=True)
    args = parser.parse_args()

    if args.wait_pid:
        print(f"Waiting for existing retry process {args.wait_pid}.", flush=True)
        while True:
            try:
                os.kill(args.wait_pid, 0)
            # Windows raises SystemError for signal 0 even when the target is
            # already gone; either exception means it is safe to continue.
            except (OSError, SystemError):
                break
            time.sleep(5)

    output_csv = ROOT / args.output_csv
    state_file = ROOT / args.state_file
    round_number = 0
    while True:
        completed, errors = count_rows(output_csv)
        if completed >= args.target and errors == 0:
            write_state(state_file, round_number=round_number, completed=completed, errors=errors, target=args.target, status="complete")
            print("All target rows completed.", flush=True)
            return

        round_number += 1
        write_state(state_file, round_number=round_number, completed=completed, errors=errors, target=args.target, status="running")
        print(f"Starting retry round {round_number}: {completed}/{args.target} complete, {errors} errors.", flush=True)
        command = [
            sys.executable,
            "scripts/run_asr_evaluation.py",
            "--folder", args.folder,
            "--provider", args.provider,
            "--model", args.model,
            "--ground-truth", args.ground_truth,
            "--quality-csv", args.quality_csv,
            "--limit", "0",
            "--language", args.language,
            "--output-csv", args.output_csv,
            "--output-jsonl", args.output_jsonl,
            "--resume",
            "--checkpoint-every", "1",
            "--max-retries", str(args.max_retries),
            "--retry-delay", str(args.retry_delay),
            "--request-delay", str(args.request_delay),
            "--only-ground-truth",
        ]
        subprocess.run(command, cwd=ROOT, check=False)
        completed, errors = count_rows(output_csv)
        if completed >= args.target and errors == 0:
            write_state(state_file, round_number=round_number, completed=completed, errors=errors, target=args.target, status="complete")
            print("All target rows completed.", flush=True)
            return

        write_state(state_file, round_number=round_number, completed=completed, errors=errors, target=args.target, status=f"cooldown {args.cooldown_seconds}s")
        print(f"Round {round_number} finished: {completed}/{args.target} complete, {errors} errors; cooling down.", flush=True)
        time.sleep(args.cooldown_seconds)


if __name__ == "__main__":
    main()

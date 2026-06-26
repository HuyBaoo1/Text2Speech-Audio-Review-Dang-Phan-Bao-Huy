"""Run the remaining Gemini models sequentially, then refresh README."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIGS = (
    "configs/benchmark_gemini_remaining_matched.json",
    "configs/benchmark_gemini_remaining_studio.json",
)


def main() -> None:
    exit_code = 0
    for config in CONFIGS:
        command = [
            sys.executable,
            "scripts/run_openai_parallel_benchmark.py",
            "--config",
            config,
            "--no-update-readme",
        ]
        print(f"Starting {config}", flush=True)
        exit_code = max(exit_code, subprocess.run(command, cwd=ROOT).returncode)
    subprocess.run([sys.executable, "scripts/update_studio_groq_readme.py"], cwd=ROOT, check=False)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

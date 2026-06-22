"""Run independent ASR models concurrently and persist a resumable leaderboard."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Semaphore
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}
KEY_ALIASES = {
    "OPENAI_API_KEY": ("OPENAI_API_KEY", "OPEN_API_KEY"),
    "GROQ_API_KEY": ("GROQ_API_KEY",),
}

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def benchmark_python() -> str:
    venv_python = ROOT / "venv" / "Scripts" / "python.exe"
    return str(venv_python) if venv_python.exists() else sys.executable


def atomic_write(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding=encoding, delete=False, dir=path.parent, suffix=".tmp") as handle:
        temp_path = Path(handle.name)
        handle.write(content)
    os.replace(temp_path, path)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def configured(item: dict[str, Any]) -> bool:
    required = item.get("required_env", [])
    if isinstance(required, str):
        required = [required]
    for name in required:
        aliases = KEY_ALIASES.get(name, (name,))
        if not any(os.getenv(alias, "").strip() and not os.getenv(alias, "").startswith("put-your") for alias in aliases):
            return False
    return True


def output_paths(config: dict[str, Any], item: dict[str, Any]) -> dict[str, Path]:
    output_dir = ROOT / config.get("output_dir", "outputs")
    prefix = config.get("output_prefix", "openai_parallel_asr_eval")
    name = item["name"]
    return {
        "csv": output_dir / f"{prefix}_{name}.csv",
        "jsonl": output_dir / f"{prefix}_{name}.jsonl",
        "log": output_dir / f"{prefix}_{name}.log",
    }


def child_command(config: dict[str, Any], item: dict[str, Any], checkpoint_every: int) -> list[str]:
    paths = output_paths(config, item)
    command = [
        benchmark_python(),
        "scripts/run_asr_evaluation.py",
        "--folder", config["dataset_folder"],
        "--provider", item["provider"],
        "--model", item["model"],
        "--ground-truth", config["ground_truth"],
        "--quality-csv", config.get("quality_csv", "outputs/quality_report.csv"),
        "--limit", str(config.get("limit", 0)),
        "--language", item.get("language", config.get("language", "vi")),
        "--output-csv", str(paths["csv"].relative_to(ROOT)),
        "--output-jsonl", str(paths["jsonl"].relative_to(ROOT)),
        "--resume",
        "--checkpoint-every", str(checkpoint_every),
        "--max-retries", str(item.get("max_retries", config.get("max_retries", 5))),
        "--retry-delay", str(item.get("retry_delay", config.get("retry_delay", 3))),
        "--request-delay", str(item.get("request_delay", config.get("request_delay", 0))),
    ]
    if config.get("only_ground_truth"):
        command.append("--only-ground-truth")
    return command


def run_one(
    config: dict[str, Any], item: dict[str, Any], checkpoint_every: int, provider_gate: Semaphore | None = None
) -> tuple[str, int]:
    paths = output_paths(config, item)
    paths["log"].parent.mkdir(parents=True, exist_ok=True)
    command = child_command(config, item, checkpoint_every)
    if provider_gate:
        provider_gate.acquire()
    try:
        print(f"START {item['name']}: {' '.join(command)}", flush=True)
        with open(paths["log"], "a", encoding="utf-8") as log:
            log.write(f"\n[{utc_now()}] START {' '.join(command)}\n")
            process = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            log.write(f"[{utc_now()}] EXIT {process.returncode}\n")
        print(f"DONE {item['name']}: exit={process.returncode}", flush=True)
        return item["name"], process.returncode
    finally:
        if provider_gate:
            provider_gate.release()


def target_count(config: dict[str, Any]) -> int:
    folder = ROOT / config["dataset_folder"]
    ground_truth = ROOT / config["ground_truth"]
    audio_paths = sorted(path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES)
    if config.get("only_ground_truth"):
        audio_paths = [
            path
            for path in audio_paths
            if (ground_truth / f"{path.stem}.txt").exists()
            and (ground_truth / f"{path.stem}.txt").read_text(encoding="utf-8").strip()
        ]
    limit = int(config.get("limit", 0))
    return len(audio_paths[:limit]) if limit else len(audio_paths)


def read_metrics(config: dict[str, Any], item: dict[str, Any], target: int) -> dict[str, Any]:
    paths = output_paths(config, item)
    rows: list[dict[str, str]] = []
    if paths["csv"].exists():
        with open(paths["csv"], encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    error_rows = [row for row in rows if row.get("manual_notes", "").startswith("ERROR:")]
    completed = [row for row in rows if row.get("source_file") and row not in error_rows]
    scored = [row for row in completed if row.get("wer") and row.get("cer")]
    wers = [float(row["wer"]) for row in scored]
    cers = [float(row["cer"]) for row in scored]
    return {
        "name": item["name"],
        "provider": item["provider"],
        "model": item["model"],
        "label": item.get("label", f"{item['provider']} `{item['model']}`"),
        "target": target,
        "completed": len(completed),
        "scored": len(scored),
        "errors": len(error_rows),
        "empty": sum(not row.get("hypothesis", "").strip() for row in scored),
        "wer_avg": sum(wers) / len(wers) if wers else None,
        "cer_avg": sum(cers) / len(cers) if cers else None,
        "csv": str(paths["csv"].relative_to(ROOT)),
        "jsonl": str(paths["jsonl"].relative_to(ROOT)),
        "log": str(paths["log"].relative_to(ROOT)),
    }


def ranked(metrics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = [row for row in metrics if row["wer_avg"] is not None]
    ineligible = [row for row in metrics if row["wer_avg"] is None]
    eligible.sort(key=lambda row: (row["wer_avg"], row["cer_avg"], -row["completed"]))
    for rank, row in enumerate(eligible, start=1):
        row["rank"] = str(rank)
    for row in ineligible:
        row["rank"] = "-"
    return eligible + ineligible


def markdown_table(metrics: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Rank | Model | Coverage | WER | CER | Kết luận |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in metrics:
        score = "chưa có điểm" if row["wer_avg"] is None else f"{row['wer_avg']:.4f}"
        cer = "-" if row["cer_avg"] is None else f"{row['cer_avg']:.4f}"
        if row["errors"]:
            verdict = f"{row['errors']} lỗi API; lần sau sẽ retry các dòng lỗi"
        elif row["empty"]:
            verdict = f"{row['empty']} empty output"
        elif row["wer_avg"] is None:
            verdict = "Chưa có kết quả để xếp hạng"
        elif row["completed"] < row["target"]:
            verdict = "Partial, có thể resume"
        else:
            verdict = "Hoàn tất"
        lines.append(
            f"| {row['rank']} | {row['label']} | {row['completed']}/{row['target']} | {score} | {cer} | {verdict} |"
        )
    return lines


def general_comments(metrics: list[dict[str, Any]]) -> list[str]:
    scored = [row for row in metrics if row["wer_avg"] is not None]
    if not scored:
        return ["- Chưa có model nào có điểm WER/CER; xem log từng model, rồi chạy lại cùng lệnh để resume."]
    best = scored[0]
    comments = [
        f"- **Tốt nhất trong lượt chạy này:** {best['label']} (WER {best['wer_avg']:.4f}, CER {best['cer_avg']:.4f}).",
    ]
    incomplete = [row for row in metrics if row["completed"] < row["target"]]
    if incomplete:
        comments.append("- Các model chưa đủ coverage sẽ tự tiếp tục từ checkpoint; các dòng đã hoàn tất không bị gọi lại.")
    if any(row["empty"] for row in metrics):
        comments.append("- Cần xem lại model có empty output trước khi dùng transcript cho TTS.")
    return comments


def update_readme(section: str, marker: str) -> None:
    readme = ROOT / "README.md"
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    content = readme.read_text(encoding="utf-8")
    replacement = f"{start}\n{section.rstrip()}\n{end}"
    if start not in content or end not in content:
        raise RuntimeError(f"README.md is missing the {marker} markers.")
    before, remainder = content.split(start, 1)
    _, after = remainder.split(end, 1)
    atomic_write(readme, before + replacement + after)


def summarize(config: dict[str, Any], update_readme_file: bool) -> None:
    target = target_count(config)
    metrics = ranked([read_metrics(config, item, target) for item in config["models"]])
    output_dir = ROOT / config.get("output_dir", "outputs")
    summary_csv = output_dir / config.get("summary_csv", "openai_parallel_benchmark_summary.csv")
    summary_md = output_dir / config.get("summary_md", "openai_parallel_benchmark.md")
    fields = ["rank", "name", "provider", "model", "target", "completed", "scored", "errors", "empty", "wer_avg", "cer_avg", "csv", "jsonl", "log"]
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=output_dir, suffix=".tmp") as handle:
        temp_path = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(metrics)
    os.replace(temp_path, summary_csv)

    report_title = config.get("report_title", "OpenAI Parallel Benchmark")
    section = "\n".join(
        [
            f"### {report_title} (Generated)",
            "",
            "Các model được chạy đồng thời; mỗi model checkpoint sau từng audio và có thể resume bằng cùng lệnh.",
            "",
            *markdown_table(metrics),
            "",
            "Kết luận ngắn:",
            *general_comments(metrics),
        ]
    )
    report = "\n".join([f"# {report_title}", "", f"Generated: {utc_now()}", "", section, ""])
    atomic_write(summary_md, report, encoding="utf-8-sig")
    if update_readme_file:
        update_readme(section, config.get("readme_marker", "OPENAI_PARALLEL_BENCHMARK"))
    print(f"Wrote {summary_csv.relative_to(ROOT)}")
    print(f"Wrote {summary_md.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run configured OpenAI/Groq ASR models concurrently with resumable checkpoints")
    parser.add_argument("--config", default="configs/benchmark_openai_parallel_vi.json")
    parser.add_argument("--max-workers", type=int, default=None, help="Concurrent model processes (default: config or all models)")
    parser.add_argument("--checkpoint-every", type=int, default=None, help="Persist every N completed audio files (default: config, usually 1)")
    parser.add_argument("--summary-only", action="store_true", help="Regenerate ranking/README from existing checkpoints without API calls")
    parser.add_argument("--no-update-readme", action="store_true", help="Write output report but leave README.md unchanged")
    args = parser.parse_args()

    config_path = ROOT / args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir = ROOT / config.get("output_dir", "outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / config.get("state_json", "openai_parallel_benchmark_state.json")
    checkpoint_every = args.checkpoint_every or int(config.get("checkpoint_every", 1))

    if not args.summary_only:
        state: dict[str, Any] = {"updated_at": utc_now(), "config": args.config, "models": {}}
        runnable: list[dict[str, Any]] = []
        for item in config["models"]:
            paths = output_paths(config, item)
            model_state = {"status": "running" if configured(item) else "skipped_missing_key", **{key: str(value.relative_to(ROOT)) for key, value in paths.items()}}
            state["models"][item["name"]] = model_state
            if configured(item):
                runnable.append(item)
        atomic_write_json(state_path, state)

        workers = args.max_workers or int(config.get("max_workers", len(runnable) or 1))
        provider_limits = config.get("provider_concurrency", {})
        gates = {name: Semaphore(int(limit)) for name, limit in provider_limits.items()}
        with ThreadPoolExecutor(max_workers=max(1, min(workers, len(runnable) or 1))) as executor:
            futures = {
                executor.submit(
                    run_one,
                    config,
                    item,
                    checkpoint_every,
                    gates.get(item.get("concurrency_group", item["provider"])),
                ): item
                for item in runnable
            }
            for future in as_completed(futures):
                item = futures[future]
                _, return_code = future.result()
                state["models"][item["name"]].update({"status": "ok" if return_code == 0 else "failed", "return_code": return_code, "finished_at": utc_now()})
                state["updated_at"] = utc_now()
                atomic_write_json(state_path, state)

    summarize(config, update_readme_file=not args.no_update_readme)


if __name__ == "__main__":
    main()

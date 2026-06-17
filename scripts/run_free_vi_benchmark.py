import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


KEY_ALIASES = {
    "OPENAI_API_KEY": ["OPENAI_API_KEY", "OPEN_API_KEY"],
    "GROQ_API_KEY": ["GROQ_API_KEY"],
    "DEEPGRAM_API_KEY": ["DEEPGRAM_API_KEY"],
    "GEMINI_API_KEY": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "ELEVENLABS_API_KEY": ["ELEVENLABS_API_KEY", "XI_API_KEY"],
    "AZURE_SPEECH_KEY": ["AZURE_SPEECH_KEY", "SPEECH_KEY"],
    "IFLYTEK_APP_ID": ["IFLYTEK_APP_ID"],
    "IFLYTEK_API_KEY": ["IFLYTEK_API_KEY"],
    "IFLYTEK_API_SECRET": ["IFLYTEK_API_SECRET"],
}


def has_key(env_name: str | None) -> bool:
    if not env_name:
        return True
    for key in KEY_ALIASES.get(env_name, [env_name]):
        value = os.getenv(key, "").strip()
        if value and not value.startswith("put-your"):
            return True
    return False


def missing_env_names(item: dict[str, object]) -> list[str]:
    required = item.get("required_env") or item.get("free_quota_env")
    if not required:
        return []
    env_names = required if isinstance(required, list) else [str(required)]
    return [env_name for env_name in env_names if not has_key(str(env_name))]


def score_summary(scored_csv: Path) -> dict[str, str]:
    if not scored_csv.exists():
        return {"matched": "0", "wer_avg": "", "cer_avg": ""}
    with open(scored_csv, encoding="utf-8", newline="") as f:
        rows = [row for row in csv.DictReader(f) if row.get("wer")]
    wers = [float(row["wer"]) for row in rows]
    cers = [float(row["cer"]) for row in rows]
    return {
        "matched": str(len(rows)),
        "wer_avg": f"{sum(wers) / len(wers):.6f}" if wers else "",
        "cer_avg": f"{sum(cers) / len(cers):.6f}" if cers else "",
        "wer_min": f"{min(wers):.6f}" if wers else "",
        "wer_max": f"{max(wers):.6f}" if wers else "",
    }


def run_command(command: list[str]) -> int:
    print(" ".join(command))
    process = subprocess.run(command, cwd=ROOT)
    return process.returncode


def run_benchmark(config_path: str, only_configured: bool, skip_local: bool) -> None:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    results = []

    for item in config["models"]:
        name = item["name"]
        provider = item["provider"]
        model = item["model"]
        is_local = provider == "local-whisper"

        if skip_local and is_local:
            print(f"SKIP {name}: local model skipped")
            results.append({"name": name, "provider": provider, "model": model, "status": "skipped_local"})
            continue

        missing_env = missing_env_names(item)
        if only_configured and not is_local and missing_env:
            missing_label = "+".join(missing_env)
            print(f"SKIP {name}: missing {missing_label}")
            results.append({"name": name, "provider": provider, "model": model, "status": f"missing_{missing_label}"})
            continue

        output_dir = Path(config.get("output_dir", "outputs"))
        output_prefix = config.get("output_prefix", "asr_eval")
        output_csv = output_dir / f"{output_prefix}_{name}.csv"
        output_jsonl = output_dir / f"{output_prefix}_{name}.jsonl"
        scored_csv = output_dir / f"{output_prefix}_{name}_scored.csv"
        command = [
            sys.executable,
            "scripts/run_asr_evaluation.py",
            "--folder",
            config["dataset_folder"],
            "--provider",
            provider,
            "--model",
            model,
            "--ground-truth",
            config["ground_truth"],
            "--quality-csv",
            config["quality_csv"],
            "--limit",
            str(config["limit"]),
            "--language",
            item.get("language", os.getenv("ASR_LANGUAGE", "vi")),
            "--output-csv",
            str(output_csv),
            "--output-jsonl",
            str(output_jsonl),
            "--resume",
            "--checkpoint-every",
            "10",
        ]
        if config.get("only_ground_truth"):
            command.append("--only-ground-truth")
        status = "ok" if run_command(command) == 0 else "failed"
        if status == "ok":
            score_command = [
                sys.executable,
                "scripts/score_existing_asr.py",
                "--input-csv",
                str(output_csv),
                "--output-csv",
                str(scored_csv),
                "--output-jsonl",
                str(output_dir / f"{output_prefix}_{name}_scored.jsonl"),
                "--ground-truth",
                config["ground_truth"],
            ]
            status = "ok" if run_command(score_command) == 0 else "score_failed"
        summary = score_summary(scored_csv)
        results.append({"name": name, "provider": provider, "model": model, "status": status, **summary})

    output = ROOT / config.get("summary_csv", "outputs/benchmark_free_vi_summary.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["name", "provider", "model", "status", "matched", "wer_avg", "cer_avg", "wer_min", "wer_max"]
    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Vietnamese ASR benchmark using local/free-quota models only")
    parser.add_argument("--config", default="configs/benchmark_free_vi.json")
    parser.add_argument("--only-configured", action="store_true", default=True)
    parser.add_argument("--skip-local", action="store_true", help="Skip local model downloads/runs")
    args = parser.parse_args()
    run_benchmark(args.config, only_configured=args.only_configured, skip_local=args.skip_local)

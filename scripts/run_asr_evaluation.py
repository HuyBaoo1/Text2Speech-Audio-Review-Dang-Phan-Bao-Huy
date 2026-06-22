import argparse
import csv
import json
import os
import sys
import tempfile
import time
import wave
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from tts_data_pipeline.asr import (
    compare_transcriptions,
    transcribe_azure_api,
    transcribe_deepgram_api,
    transcribe_elevenlabs_api,
    transcribe_gemini_api,
    transcribe_groq_api,
    transcribe_iflytek_api,
    transcribe_openai_api,
    transcribe_openai_realtime_api,
    transcribe_whisper_local,
)
from tts_data_pipeline.pipeline import normalize_text, scan_audio_files, strip_ground_truth_annotations


FIELDNAMES = [
    "path",
    "source_file",
    "provider",
    "model",
    "duration",
    "pass_quality_gate",
    "reference",
    "hypothesis",
    "wer",
    "cer",
    "manual_accept",
    "manual_error_tags",
    "manual_notes",
]


def read_reference(ground_truth: str, audio_path: str) -> str | None:
    ref_path = Path(ground_truth) / f"{Path(audio_path).stem}.txt"
    if not ref_path.exists():
        return None
    return normalize_text(strip_ground_truth_annotations(ref_path.read_text(encoding="utf-8")))


def load_quality_index(quality_csv: str) -> dict[str, dict[str, str]]:
    path = Path(quality_csv)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row["path"]: row for row in rows}


def wav_duration(path: str) -> str:
    try:
        with wave.open(path, "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            return f"{frames / float(rate):.3f}" if rate else ""
    except wave.Error:
        return ""


def select_audio_paths(folder: str, limit: int, ground_truth: str, only_ground_truth: bool) -> list[str]:
    audio_paths = scan_audio_files(folder, limit=None)
    if only_ground_truth:
        gt_dir = Path(ground_truth)
        gt_stems = {
            path.stem
            for path in gt_dir.glob("*.txt")
            if path.read_text(encoding="utf-8").strip()
        }
        audio_paths = [path for path in audio_paths if Path(path).stem in gt_stems]
    return audio_paths[:limit] if limit else audio_paths


def transcribe(
    path: str,
    provider: str,
    model: str,
    openai_api_key: str | None,
    groq_api_key: str | None,
    deepgram_api_key: str | None,
    gemini_api_key: str | None,
    elevenlabs_api_key: str | None,
    azure_speech_key: str | None,
    azure_speech_region: str | None,
    iflytek_app_id: str | None,
    iflytek_api_key: str | None,
    iflytek_api_secret: str | None,
    language: str | None,
) -> str:
    if provider == "local-whisper":
        return transcribe_whisper_local(path, model_name=model)
    if provider == "openai":
        return transcribe_openai_api(path, openai_api_key=openai_api_key, model=model)
    if provider == "openai-realtime":
        return transcribe_openai_realtime_api(
            path,
            openai_api_key=openai_api_key,
            model=model,
            language=language,
        )
    if provider == "groq":
        return transcribe_groq_api(path, groq_api_key=groq_api_key, model=model)
    if provider == "deepgram":
        return transcribe_deepgram_api(path, deepgram_api_key=deepgram_api_key, model=model, language=language)
    if provider == "gemini":
        return transcribe_gemini_api(path, gemini_api_key=gemini_api_key, model=model, language=language)
    if provider == "elevenlabs":
        return transcribe_elevenlabs_api(
            path,
            elevenlabs_api_key=elevenlabs_api_key,
            model=model,
            language=language,
        )
    if provider == "azure":
        return transcribe_azure_api(
            path,
            azure_speech_key=azure_speech_key,
            azure_speech_region=azure_speech_region,
            model=model,
            language=language,
        )
    if provider == "iflytek":
        return transcribe_iflytek_api(
            path,
            iflytek_app_id=iflytek_app_id,
            iflytek_api_key=iflytek_api_key,
            iflytek_api_secret=iflytek_api_secret,
            model=model,
            language=language,
        )
    raise ValueError(f"Unsupported provider: {provider}")


def is_error_row(row: dict[str, str]) -> bool:
    return row.get("manual_notes", "").startswith("ERROR:")


def prefer_resume_row(current: dict[str, str] | None, candidate: dict[str, str]) -> dict[str, str]:
    if current is None:
        return candidate
    if is_error_row(current) and not is_error_row(candidate):
        return candidate
    if not is_error_row(current) and is_error_row(candidate):
        return current
    return candidate


def load_existing_rows(output_csv: str) -> list[dict[str, str]]:
    path = Path(output_csv)
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    deduped_by_source: dict[str, dict[str, str]] = {}
    passthrough_rows: list[dict[str, str]] = []
    for row in rows:
        source_file = row.get("source_file")
        if not source_file:
            passthrough_rows.append(row)
            continue
        deduped_by_source[source_file] = prefer_resume_row(deduped_by_source.get(source_file), row)
    return passthrough_rows + list(deduped_by_source.values())


def write_outputs(output_csv: str, output_jsonl: str, rows: list[dict[str, str]]) -> None:
    def replace_checkpoint(temp_path: Path, destination: Path) -> None:
        for attempt in range(6):
            try:
                os.replace(temp_path, destination)
                return
            except PermissionError:
                if attempt == 5:
                    raise
                time.sleep(0.2 * (attempt + 1))

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Write then replace so a timeout never leaves a partially-written checkpoint.
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8-sig", newline="", delete=False, dir=output_path.parent, suffix=".tmp"
    ) as f:
        csv_temp = Path(f.name)
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    replace_checkpoint(csv_temp, output_path)

    jsonl_path = Path(output_jsonl)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir=jsonl_path.parent, suffix=".tmp"
    ) as f:
        jsonl_temp = Path(f.name)
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    replace_checkpoint(jsonl_temp, jsonl_path)


def run_asr_evaluation(
    folder: str,
    provider: str,
    model: str,
    output_csv: str,
    output_jsonl: str,
    ground_truth: str,
    quality_csv: str,
    limit: int,
    openai_api_key: str | None,
    groq_api_key: str | None,
    deepgram_api_key: str | None,
    gemini_api_key: str | None,
    elevenlabs_api_key: str | None,
    azure_speech_key: str | None,
    azure_speech_region: str | None,
    iflytek_app_id: str | None,
    iflytek_api_key: str | None,
    iflytek_api_secret: str | None,
    language: str | None,
    only_ground_truth: bool,
    resume: bool,
    checkpoint_every: int,
    max_retries: int,
    retry_delay: float,
    request_delay: float,
) -> None:
    rows = load_existing_rows(output_csv) if resume else []
    completed = {
        row["source_file"]
        for row in rows
        if row.get("source_file") and not row.get("manual_notes", "").startswith("ERROR:")
    }
    audio_paths = select_audio_paths(folder, limit=limit, ground_truth=ground_truth, only_ground_truth=only_ground_truth)
    quality_index = load_quality_index(quality_csv)
    print(f"Running ASR on {len(audio_paths)} audio files from {folder}")
    if resume:
        print(f"Resume enabled: loaded {len(rows)} deduped rows, skipping {len(completed)} completed files")

    processed_since_checkpoint = 0
    for index, path in enumerate(audio_paths, start=1):
        source_file = Path(path).name
        if source_file in completed:
            continue
        quality = quality_index.get(path, {})
        error_note = ""
        for attempt in range(max_retries + 1):
            try:
                hypothesis = normalize_text(
                    transcribe(
                        path,
                        provider,
                        model,
                        openai_api_key=openai_api_key,
                        groq_api_key=groq_api_key,
                        deepgram_api_key=deepgram_api_key,
                        gemini_api_key=gemini_api_key,
                        elevenlabs_api_key=elevenlabs_api_key,
                        azure_speech_key=azure_speech_key,
                        azure_speech_region=azure_speech_region,
                        iflytek_app_id=iflytek_app_id,
                        iflytek_api_key=iflytek_api_key,
                        iflytek_api_secret=iflytek_api_secret,
                        language=language,
                    )
                )
                break
            except Exception as exc:
                retryable = (
                    getattr(exc, "status_code", None) in {408, 409, 429, 500, 502, 503, 504}
                    or any(token in str(exc).lower() for token in ("rate limit", "timeout", "connection", "temporar"))
                )
                if retryable and attempt < max_retries:
                    delay = retry_delay * (2**attempt)
                    print(f"{Path(path).name}: retry {attempt + 1}/{max_retries} after {delay:.1f}s ({type(exc).__name__})")
                    time.sleep(delay)
                    continue
                hypothesis = ""
                error_note = f"ERROR: {type(exc).__name__}: {str(exc)[:300]}"
                print(f"{Path(path).name}: {error_note}")
                break

        reference = read_reference(ground_truth, path)
        wer_score = ""
        cer_score = ""

        if reference and not error_note:
            stats = compare_transcriptions(reference, hypothesis)
            wer_score = f"{stats['wer']:.6f}"
            cer_score = f"{stats['cer']:.6f}"

        row = {
            "path": path,
            "source_file": source_file,
            "provider": provider,
            "model": model,
            "duration": quality.get("duration") or wav_duration(path),
            "pass_quality_gate": quality.get("pass_quality_gate", ""),
            "reference": reference or "",
            "hypothesis": hypothesis,
            "wer": wer_score,
            "cer": cer_score,
            "manual_accept": "",
            "manual_error_tags": "",
            "manual_notes": error_note,
        }
        rows = [existing for existing in rows if existing.get("source_file") != source_file]
        rows.append(row)
        if not error_note:
            print(f"{source_file}: {hypothesis[:120]}")
        processed_since_checkpoint += 1
        if checkpoint_every > 0 and processed_since_checkpoint >= checkpoint_every:
            write_outputs(output_csv, output_jsonl, rows)
            print(f"Checkpoint: {len(rows)} rows written after source index {index}")
            processed_since_checkpoint = 0
        if request_delay > 0:
            time.sleep(request_delay)

    write_outputs(output_csv, output_jsonl, rows)
    print(f"Wrote {output_csv}")
    print(f"Wrote {output_jsonl}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ASR model comparison on matched audio samples")
    parser.add_argument("--folder", default="audio_samples/matched_audio")
    parser.add_argument(
        "--provider",
        choices=["local-whisper", "openai", "openai-realtime", "groq", "deepgram", "gemini", "elevenlabs", "azure", "iflytek"],
        default="local-whisper",
    )
    parser.add_argument("--model", default="openai/whisper-small")
    parser.add_argument("--ground-truth", default="data/ground_truth")
    parser.add_argument("--quality-csv", default="outputs/quality_report.csv")
    parser.add_argument("--output-csv", default="outputs/asr_eval.csv")
    parser.add_argument("--output-jsonl", default="outputs/asr_eval.jsonl")
    parser.add_argument("--limit", type=int, default=0, help="Maximum files to run; 0 means the full selected dataset")
    parser.add_argument("--only-ground-truth", action="store_true", help="Run only audio files that have non-empty ground truth")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing output CSV and skip completed files")
    parser.add_argument("--checkpoint-every", type=int, default=10, help="Write output every N new rows; use 0 to write only at end")
    parser.add_argument("--max-retries", type=int, default=3, help="Retry transient API/rate-limit failures this many times")
    parser.add_argument("--retry-delay", type=float, default=3.0, help="Initial retry delay in seconds; retries use exponential backoff")
    parser.add_argument("--request-delay", type=float, default=0.0, help="Wait this many seconds after each audio request")
    parser.add_argument("--language", default=os.getenv("ASR_LANGUAGE", "vi"))
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY"))
    parser.add_argument("--groq-api-key", default=os.getenv("GROQ_API_KEY"))
    parser.add_argument("--deepgram-api-key", default=os.getenv("DEEPGRAM_API_KEY"))
    parser.add_argument("--gemini-api-key", default=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    parser.add_argument("--elevenlabs-api-key", default=os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY"))
    parser.add_argument("--azure-speech-key", default=os.getenv("AZURE_SPEECH_KEY") or os.getenv("SPEECH_KEY"))
    parser.add_argument("--azure-speech-region", default=os.getenv("AZURE_SPEECH_REGION") or os.getenv("SPEECH_REGION"))
    parser.add_argument("--iflytek-app-id", default=os.getenv("IFLYTEK_APP_ID"))
    parser.add_argument("--iflytek-api-key", default=os.getenv("IFLYTEK_API_KEY"))
    parser.add_argument("--iflytek-api-secret", default=os.getenv("IFLYTEK_API_SECRET"))
    args = parser.parse_args()
    run_asr_evaluation(
        folder=args.folder,
        provider=args.provider,
        model=args.model,
        output_csv=args.output_csv,
        output_jsonl=args.output_jsonl,
        ground_truth=args.ground_truth,
        quality_csv=args.quality_csv,
        limit=args.limit,
        openai_api_key=args.openai_api_key,
        groq_api_key=args.groq_api_key,
        deepgram_api_key=args.deepgram_api_key,
        gemini_api_key=args.gemini_api_key,
        elevenlabs_api_key=args.elevenlabs_api_key,
        azure_speech_key=args.azure_speech_key,
        azure_speech_region=args.azure_speech_region,
        iflytek_app_id=args.iflytek_app_id,
        iflytek_api_key=args.iflytek_api_key,
        iflytek_api_secret=args.iflytek_api_secret,
        language=args.language,
        only_ground_truth=args.only_ground_truth,
        resume=args.resume,
        checkpoint_every=args.checkpoint_every,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        request_delay=args.request_delay,
    )

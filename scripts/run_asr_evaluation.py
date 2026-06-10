import argparse
import csv
import json
import os
import sys
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
    transcribe_openai_api,
    transcribe_whisper_local,
)
from tts_data_pipeline.pipeline import normalize_text, scan_audio_files


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
    return normalize_text(ref_path.read_text(encoding="utf-8"))


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
    language: str | None,
) -> str:
    if provider == "local-whisper":
        return transcribe_whisper_local(path, model_name=model)
    if provider == "openai":
        return transcribe_openai_api(path, openai_api_key=openai_api_key, model=model)
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
    raise ValueError(f"Unsupported provider: {provider}")


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
    language: str | None,
    only_ground_truth: bool,
) -> None:
    rows = []
    audio_paths = select_audio_paths(folder, limit=limit, ground_truth=ground_truth, only_ground_truth=only_ground_truth)
    quality_index = load_quality_index(quality_csv)
    print(f"Running ASR on {len(audio_paths)} audio files from {folder}")

    for path in audio_paths:
        quality = quality_index.get(path, {})
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
                language=language,
            )
        )
        reference = read_reference(ground_truth, path)
        wer_score = ""
        cer_score = ""

        if reference:
            stats = compare_transcriptions(reference, hypothesis)
            wer_score = f"{stats['wer']:.6f}"
            cer_score = f"{stats['cer']:.6f}"

        rows.append(
            {
                "path": path,
                "source_file": Path(path).name,
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
                "manual_notes": "",
            }
        )
        print(f"{Path(path).name}: {hypothesis[:120]}")

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    jsonl_path = Path(output_jsonl)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {output_csv}")
    print(f"Wrote {output_jsonl}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ASR model comparison on the first N matched audio samples")
    parser.add_argument("--folder", default="audio_samples/matched_audio")
    parser.add_argument(
        "--provider",
        choices=["local-whisper", "openai", "groq", "deepgram", "gemini", "elevenlabs", "azure"],
        default="local-whisper",
    )
    parser.add_argument("--model", default="openai/whisper-small")
    parser.add_argument("--ground-truth", default="data/ground_truth")
    parser.add_argument("--quality-csv", default="outputs/quality_report.csv")
    parser.add_argument("--output-csv", default="outputs/asr_eval.csv")
    parser.add_argument("--output-jsonl", default="outputs/asr_eval.jsonl")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--only-ground-truth", action="store_true", help="Run only audio files that have non-empty ground truth")
    parser.add_argument("--language", default=os.getenv("ASR_LANGUAGE", "vi"))
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY"))
    parser.add_argument("--groq-api-key", default=os.getenv("GROQ_API_KEY"))
    parser.add_argument("--deepgram-api-key", default=os.getenv("DEEPGRAM_API_KEY"))
    parser.add_argument("--gemini-api-key", default=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    parser.add_argument("--elevenlabs-api-key", default=os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY"))
    parser.add_argument("--azure-speech-key", default=os.getenv("AZURE_SPEECH_KEY") or os.getenv("SPEECH_KEY"))
    parser.add_argument("--azure-speech-region", default=os.getenv("AZURE_SPEECH_REGION") or os.getenv("SPEECH_REGION"))
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
        language=args.language,
        only_ground_truth=args.only_ground_truth,
    )

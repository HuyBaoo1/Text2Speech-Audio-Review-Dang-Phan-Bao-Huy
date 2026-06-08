import argparse
import csv
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tts_data_pipeline.pipeline import scan_audio_files, write_csv


FIELDNAMES = [
    "path",
    "source_file",
    "speaker_id",
    "language",
    "source_url",
    "duration",
    "quality_gate",
    "manual_transcript",
    "usable_for_tts",
    "reject_reason",
    "notes",
]


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


def create_manifest(folder: str, output_csv: str, limit: int, quality_csv: str) -> None:
    quality_index = load_quality_index(quality_csv)
    rows = []
    for path in scan_audio_files(folder, limit=limit):
        quality = quality_index.get(path, {})
        rows.append(
            {
                "path": path,
                "source_file": Path(path).name,
                "speaker_id": "",
                "language": "",
                "source_url": "",
                "duration": quality.get("duration") or wav_duration(path),
                "quality_gate": "pass" if quality.get("pass_quality_gate") == "True" else "review",
                "manual_transcript": "",
                "usable_for_tts": "",
                "reject_reason": "",
                "notes": "",
            }
        )

    write_csv(output_csv, rows, FIELDNAMES)
    print(f"Wrote {output_csv} with {len(rows)} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a manual evaluation manifest from audio samples")
    parser.add_argument("--folder", default="audio_samples/matched_audio")
    parser.add_argument("--output-csv", default="data/manual_eval_manifest.csv")
    parser.add_argument("--quality-csv", default="outputs/quality_report.csv")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    create_manifest(args.folder, args.output_csv, args.limit, args.quality_csv)

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tts_data_pipeline.pipeline import build_sample_record, scan_audio_files, write_csv


FIELDNAMES = [
    "path",
    "duration",
    "sample_rate",
    "channels",
    "rms",
    "peak",
    "snr",
    "silence_ratio",
    "clipping_ratio",
    "dc_offset",
    "pass_quality_gate",
]


def run_quality_analysis(folder: str, output_csv: str, limit: int) -> None:
    rows = []
    audio_paths = scan_audio_files(folder, limit=limit)
    print(f"Analyzing {len(audio_paths)} audio files from {folder}")

    for path in audio_paths:
        sample = build_sample_record(path)
        row = {
            "path": sample.path,
            "duration": f"{sample.duration:.3f}",
            "sample_rate": sample.sample_rate,
            "channels": sample.channels,
            "rms": f"{sample.rms:.6f}",
            "peak": f"{sample.peak:.6f}",
            "snr": f"{sample.snr:.3f}",
            "silence_ratio": f"{sample.silence_ratio:.6f}",
            "clipping_ratio": f"{sample.clipping_ratio:.8f}",
            "dc_offset": f"{sample.dc_offset:.8f}",
            "pass_quality_gate": sample.pass_quality_gate,
        }
        rows.append(row)
        print(
            f"{Path(path).name}: duration={sample.duration:.2f}s "
            f"snr={sample.snr:.1f} silence={sample.silence_ratio:.2f} "
            f"gate={'PASS' if sample.pass_quality_gate else 'REVIEW'}"
        )

    write_csv(output_csv, rows, FIELDNAMES)
    print(f"Wrote {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze audio quality for TTS dataset candidates")
    parser.add_argument("--folder", default="audio_samples/matched_audio")
    parser.add_argument("--output-csv", default="outputs/quality_report.csv")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    run_quality_analysis(args.folder, args.output_csv, args.limit)

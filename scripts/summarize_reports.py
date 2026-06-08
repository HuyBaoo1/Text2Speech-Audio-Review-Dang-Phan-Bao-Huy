import argparse
import csv
from collections import Counter
from pathlib import Path


def summarize_quality(path: str) -> None:
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if not rows:
        print("No rows found")
        return

    gates = Counter(row["pass_quality_gate"] for row in rows)
    durations = [float(row["duration"]) for row in rows]
    snrs = [float(row["snr"]) for row in rows]
    print(f"rows={len(rows)}")
    print(f"quality_gate={dict(gates)}")
    print(f"duration_avg={sum(durations) / len(durations):.2f}s")
    print(f"duration_min={min(durations):.2f}s duration_max={max(durations):.2f}s")
    print(f"snr_avg={sum(snrs) / len(snrs):.2f}dB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize generated CSV reports")
    parser.add_argument("--quality-csv", default="outputs/quality_report.csv")
    args = parser.parse_args()
    summarize_quality(args.quality_csv)

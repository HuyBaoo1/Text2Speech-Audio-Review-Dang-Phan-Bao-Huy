import argparse
import csv
from pathlib import Path


def import_studio_ground_truth(input_csv: str, output_dir: str, audio_folder: str) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    audio_files = {path.name for path in Path(audio_folder).glob("*.wav")}

    imported = 0
    missing_audio = 0
    empty_text = 0
    with open(input_csv, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            audio_file = row["audio_file"].strip()
            reference = " ".join(row["reference_text"].strip().split())
            if audio_file not in audio_files:
                missing_audio += 1
                continue
            if not reference:
                empty_text += 1
                continue
            (output / f"{Path(audio_file).stem}.txt").write_text(reference + "\n", encoding="utf-8")
            imported += 1

    print(f"imported={imported}")
    print(f"missing_audio={missing_audio}")
    print(f"empty_text={empty_text}")
    print(f"output_dir={output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import normalized studio ground truth CSV into .txt files")
    parser.add_argument("--input-csv", default="data/imported_ground_truth/omni_vi_ai_ground_truth.csv")
    parser.add_argument("--output-dir", default="data/ground_truth_studio")
    parser.add_argument("--audio-folder", default="audio_samples/studio")
    args = parser.parse_args()
    import_studio_ground_truth(args.input_csv, args.output_dir, args.audio_folder)

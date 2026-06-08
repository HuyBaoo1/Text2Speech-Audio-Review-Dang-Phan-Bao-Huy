# TTS Audio Manual Evaluation

Project này dùng để đánh giá thủ công một tập sample nhỏ trước khi mở rộng pipeline tự động tạo dataset TTS từ audio internet, đặc biệt là YouTube.

Nguồn data mặc định:

```text
audio_samples/matched_audio
```

Mọi script mặc định chỉ lấy 100 audio đầu theo thứ tự tên file.

## Mục Tiêu

- Hiểu cụ thể data "chất lượng cao" cho TTS cần gì.
- Xây pipeline đánh giá audio/transcript trước khi training TTS.
- So sánh ASR open-source và API trả phí/free-quota trên cùng một tập sample.
- Tạo manifest để manual review: usable/reject, lỗi transcript, speaker/language/source.

## Cấu Trúc

```text
configs/asr_models.json          model list để thử nghiệm
data/manual_eval_manifest.csv    sheet review thủ công
data/ground_truth/               transcript thủ công: <audio_stem>.txt
docs/                            notes về data quality, pipeline, ASR protocol
outputs/                         report sinh ra từ scripts
scripts/create_manifest.py       tạo manifest cho 100 sample đầu
scripts/run_quality_analysis.py  phân tích chất lượng audio
scripts/run_asr_evaluation.py    chạy ASR và xuất CSV/JSONL
scripts/summarize_reports.py     tóm tắt quality report
src/tts_data_pipeline/           package lõi
```

## Setup

```bash
cd /d D:\TTS-audio
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Nếu chỉ muốn đọc/tạo file project thì chưa cần cài dependency. Để chạy metric audio cần `librosa`; để chạy ASR cần thêm `transformers`, `torch`, `jiwer`, hoặc `openai`.

## Chạy Workflow Đầu Tiên

1. Tạo manifest manual review:

```bash
python scripts/create_manifest.py --folder audio_samples/matched_audio --limit 100
```

2. Chạy quality analysis:

```bash
python scripts/run_quality_analysis.py --folder audio_samples/matched_audio --limit 100
python scripts/summarize_reports.py
```

3. Tạo ground truth cho một phần sample:

```text
data/ground_truth/<audio_stem>.txt
```

Ví dụ:

```text
data/ground_truth/-aCDck13cRI_14.txt
```

4. Chạy ASR local baseline:

```bash
python scripts/run_asr_evaluation.py --provider local-whisper --model openai/whisper-small --limit 100
```

5. Chạy API baseline nếu có `OPENAI_API_KEY`:

```bash
$env:OPENAI_API_KEY="..."
python scripts/run_asr_evaluation.py --provider openai --model gpt-4o-mini-transcribe --limit 100
```

6. Sau khi thêm ground truth thủ công, chấm lại report ASR đã có mà không gọi lại API:

```bash
python scripts/score_existing_asr.py --input-csv outputs/asr_eval_openai.csv --output-csv outputs/asr_eval_openai_scored.csv
```

## Output Chính

- `outputs/quality_report.csv`: audio metrics và quality gate.
- `outputs/asr_eval.csv`: transcript từ ASR, WER/CER nếu có ground truth, cột manual review.
- `outputs/asr_eval.jsonl`: format dễ dùng cho automation.
- `data/manual_eval_manifest.csv`: bảng điều phối review dataset.

## Manual Decision

Trong `manual_eval_manifest.csv`, dùng:

- `usable_for_tts=yes`: sạch, single speaker, transcript khớp, có thể dùng training.
- `usable_for_tts=maybe`: cần trim/denoise/sửa transcript.
- `usable_for_tts=no`: loại khỏi dataset.

Các `reject_reason` nên dùng ngắn và nhất quán: `music_overlap`, `multi_speaker`, `low_snr`, `clipping`, `bad_transcript`, `too_short`, `too_long`, `non_speech`, `license_risk`.

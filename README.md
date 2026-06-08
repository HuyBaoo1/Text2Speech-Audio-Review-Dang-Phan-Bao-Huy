# TTS Audio Manual Evaluation

Project này dùng để đánh giá chất lượng audio/transcript cho dataset TTS trước khi mở rộng pipeline tự động thu thập dữ liệu từ internet, đặc biệt là YouTube.

Nguồn data mặc định:

```text
audio_samples/matched_audio
```

Các script hiện tại mặc định xử lý 100 audio đầu tiên theo thứ tự tên file.

## Mục tiêu

- Xác định tiêu chí audio/transcript đủ tốt để dùng cho training TTS.
- Xây pipeline đánh giá chất lượng audio trước khi đưa vào dataset.
- So sánh kết quả ASR giữa model local open-source và API model trên cùng tập sample.
- Tạo manifest để manual review: usable/reject, lỗi transcript, speaker, language, source.

## Models sử dụng

Danh sách model thử nghiệm được lưu trong `configs/asr_models.json`:

| Provider | Model | Vai trò |
| --- | --- | --- |
| `local-whisper` | `openai/whisper-small` | Baseline local nhanh, dùng để kiểm tra khả năng chạy offline và có kết quả tham chiếu ban đầu. |
| `local-whisper` | `openai/whisper-medium` | Baseline local mạnh hơn, dùng để so sánh khi runtime chấp nhận được. |
| `openai` | `gpt-4o-mini-transcribe` | API baseline, dùng để bootstrap transcript và so sánh với ground truth thủ công. Cần `OPENAI_API_KEY`. |

Ở kết quả sơ bộ hiện tại, phần ASR đã được chấm điểm chủ yếu trên `openai:gpt-4o-mini-transcribe`.

## Phương pháp test

Project đang test theo 3 lớp:

1. **Audio quality analysis**

   Chạy metric tự động trên 100 sample đầu tiên:

   - duration
   - sample rate/channels
   - RMS/peak
   - SNR
   - silence ratio
   - clipping ratio
   - DC offset
   - quality gate pass/review

   Quality gate ban đầu:

   - duration trong khoảng 1-20s
   - SNR >= 20dB
   - silence ratio <= 0.35
   - clipping ratio <= 0.001
   - absolute DC offset <= 0.02

2. **Manual review**

   Tạo `data/manual_eval_manifest.csv` để nghe và gán nhãn:

   - `usable_for_tts=yes`: audio sạch, một speaker chính, transcript có thể khớp chính xác.
   - `usable_for_tts=maybe`: cần trim, denoise, normalize hoặc sửa transcript.
   - `usable_for_tts=no`: loại khỏi dataset do noise nặng, multi-speaker, clipping, transcript không chắc, non-speech hoặc rủi ro license.

3. **ASR evaluation**

   Với các file đã có transcript thủ công trong `data/ground_truth`, project so sánh ASR hypothesis với reference bằng:

   - WER (Word Error Rate)
   - CER (Character Error Rate)
   - manual accept/error tags cho các lỗi như hallucination, missed words, number error, name error, punctuation, code-switch.

   Script `score_existing_asr.py` cho phép chấm lại file ASR đã có mà không gọi lại API.

## Kết quả sơ bộ

Tổng hợp từ `outputs/evaluation_summary.md`:

- Dataset test: 100 clips từ `audio_samples/matched_audio`.
- Số file có ground truth để chấm ASR: 11 clips.
- Audio quality gate:
  - PASS: 50/100 clips.
  - REVIEW: 50/100 clips.
  - Duration trung bình: 16.08s.
  - Duration ngắn nhất/dài nhất: 3.24s / 30.00s.
  - SNR trung bình: 46.13 dB.
- Kết quả ASR với `openai:gpt-4o-mini-transcribe` trên 11 clips có ground truth:
  - WER trung bình: 0.2878.
  - CER trung bình: 0.1842.
  - WER tốt nhất: 0.0625.
  - WER tệ nhất: 0.6400.

Nhận xét ngắn:

- 50% sample vượt quality gate tự động; 50% còn lại cần nghe lại hoặc xử lý thêm trước khi dùng cho TTS.
- `gpt-4o-mini-transcribe` có thể dùng làm nguồn bootstrap transcript, nhưng sai số còn dao động rõ giữa các file.
- Các file có WER cao nên được manual tag lỗi trước khi tin tưởng transcription hàng loạt.
- Bước tiếp theo hợp lý là chạy thêm `openai/whisper-small` và `openai/whisper-medium` trên cùng subset ground truth để so sánh chi phí/runtime/chất lượng.

## Cấu trúc project

```text
configs/asr_models.json          danh sách model thử nghiệm
data/manual_eval_manifest.csv    sheet review thủ công
data/ground_truth/               transcript thủ công: <audio_stem>.txt
docs/                            notes về data quality, pipeline, ASR protocol
outputs/                         report sinh ra từ scripts
scripts/create_manifest.py       tạo manifest cho 100 sample đầu
scripts/run_quality_analysis.py  phân tích chất lượng audio
scripts/run_asr_evaluation.py    chạy ASR và xuất CSV/JSONL
scripts/score_existing_asr.py    chấm lại ASR output khi có thêm ground truth
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

## Workflow

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

## Output chính

- `outputs/quality_report.csv`: audio metrics và quality gate.
- `outputs/asr_eval.csv`: transcript từ ASR, WER/CER nếu có ground truth, cột manual review.
- `outputs/asr_eval.jsonl`: format dễ dùng cho automation.
- `outputs/evaluation_summary.md`: tổng hợp ngắn về chất lượng audio và ASR.
- `data/manual_eval_manifest.csv`: bảng điều phối review dataset.

## Manual decision

Trong `manual_eval_manifest.csv`, dùng:

- `usable_for_tts=yes`: sạch, single speaker, transcript khớp, có thể dùng training.
- `usable_for_tts=maybe`: cần trim/denoise/sửa transcript.
- `usable_for_tts=no`: loại khỏi dataset.

Các `reject_reason` nên dùng ngắn và nhất quán: `music_overlap`, `multi_speaker`, `low_snr`, `clipping`, `bad_transcript`, `too_short`, `too_long`, `non_speech`, `license_risk`.

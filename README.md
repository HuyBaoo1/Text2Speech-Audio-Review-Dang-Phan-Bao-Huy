# TTS Audio Manual Evaluation

Project này dùng để đánh giá chất lượng audio/transcript cho dataset TTS trước khi mở rộng pipeline tự động thu thập dữ liệu từ internet, đặc biệt là YouTube.

Nguồn data chính:

```text
audio_samples/matched_audio
audio_samples/studio
```

Khi benchmark ASR, nên dùng `--only-ground-truth` để chỉ chạy những file đã có ground truth. Với model mới hoặc provider tốn quota, dùng `--limit 300`; `--limit 0` nghĩa là chạy toàn bộ tập đã chọn.

## Mục Tiêu

- Xác định tiêu chí audio/transcript đủ tốt để training TTS.
- Xây pipeline đánh giá chất lượng audio trước khi đưa vào dataset.
- So sánh ASR local open-source và API model trên cùng một tập sample.
- Tạo manifest để manual review: usable/reject, lỗi transcript, speaker, language, source.

## Kết Quả Hiện Tại

- Ground-truth scoring đã bỏ qua mọi annotation trong dạng `<...>` trước khi tính WER/CER.
- Kết quả API đã có được giữ lại trong `outputs/studio_full_asr_eval_*.csv/jsonl`; lần sau dùng `--resume` để không chạy lại audio đã xong.
- `audio_samples/matched_audio`: benchmark ban đầu trên subset có ground-truth vẫn cho thấy OpenAI tốt nhất, Groq sát phía sau, Deepgram yếu hơn trên tập nhỏ. Chi tiết: `outputs/initial_audio_samples_evaluation.md`.
- `audio_samples/studio`: đã chấm nhanh 300 audio đầu có ground-truth từ kết quả đã lưu, không gọi API thêm. Quality: PASS 16/300, REVIEW 284/300, duration TB 8.85s, SNR TB 50.00 dB, silence ratio TB 0.408.
- Studio 300 ASR ranking:
  - #1 OpenAI `gpt-4o-mini-transcribe`: 300/300 scored, WER 0.181432, CER 0.066774, không có hypothesis rỗng.
  - #2 Groq `whisper-large-v3-turbo`: 300/300 scored, WER 0.213490, CER 0.085053, không có hypothesis rỗng.
  - #3 Deepgram `nova-3`: 300/300 scored, WER 0.225865, CER 0.128594, có 21 hypothesis rỗng.
  - #4 Gemini `gemini-2.5-flash`: 300/300 scored, WER 0.234580, CER 0.125562, có 8 hypothesis rỗng.
- Nhận định: OpenAI đang là baseline tốt nhất cho tiếng Việt trên studio; Groq là lựa chọn free/quota tốt nhưng WER cao hơn; Deepgram/Gemini cần xem kỹ các dòng rỗng trước khi dùng làm transcript tự động cho TTS.
- Report mới: `outputs/studio_300_benchmark_summary.md`, `outputs/studio_300_benchmark_summary.csv`, `outputs/studio_300_benchmark_summary.json`.

## Cấu Trúc Project

```text
configs/asr_models.json              danh sách model thử nghiệm
configs/benchmark_free_vi.json       cấu hình benchmark free/free-quota cho tiếng Việt
data/manual_eval_manifest.csv        sheet review thủ công
data/ground_truth/                   transcript thủ công: <audio_stem>.txt
docs/                                notes về data quality, pipeline, ASR protocol
outputs/                             report sinh ra từ scripts
scripts/create_manifest.py           tạo manifest cho 100 sample đầu
scripts/run_quality_analysis.py      phân tích chất lượng audio
scripts/run_asr_evaluation.py        chạy ASR và xuất CSV/JSONL
scripts/score_existing_asr.py        chấm lại ASR output khi có thêm ground truth
scripts/run_free_vi_benchmark.py     chạy benchmark free/free-quota theo config
scripts/generate_evaluation_summary.py sinh Markdown summary
scripts/generate_studio_300_benchmark_summary.py sinh summary 300 audio studio từ output đã lưu
src/tts_data_pipeline/               package lõi
```

## Setup

```bash
cd /d D:\TTS-audio
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

File `.env` hỗ trợ các key sau:

```env
OPENAI_API_KEY=...
GROQ_API_KEY=...
DEEPGRAM_API_KEY=...
GEMINI_API_KEY=...
ELEVENLABS_API_KEY=...
AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=southeastasia
ASR_LANGUAGE=vi
```

## Workflow Chính

1. Tạo manifest manual review nhanh:

```bash
python scripts/create_manifest.py --folder audio_samples/matched_audio --limit 100
```

2. Chạy quality analysis:

```bash
python scripts/run_quality_analysis.py --folder audio_samples/matched_audio --limit 100
python scripts/summarize_reports.py
```

3. Tạo ground truth thủ công:

```text
data/ground_truth/<audio_stem>.txt
```

Ví dụ:

```text
data/ground_truth/-aCDck13cRI_14.txt
```

4. Chạy ASR trên những file đã có ground truth:

```bash
python scripts/run_asr_evaluation.py --folder audio_samples/studio --provider groq --model whisper-large-v3-turbo --ground-truth data/ground_truth_studio --quality-csv outputs/studio_full_quality_report.csv --limit 300 --language vi --output-csv outputs/studio_300_asr_eval_groq_whisper_large_v3_turbo.csv --output-jsonl outputs/studio_300_asr_eval_groq_whisper_large_v3_turbo.jsonl --only-ground-truth --resume --checkpoint-every 10
```

5. Chấm lại Studio 300 từ các output đã có mà không gọi API:

```bash
python scripts/generate_studio_300_benchmark_summary.py
```

6. Chạy benchmark free/free-quota:

```bash
python scripts/run_free_vi_benchmark.py
```

Nếu không muốn chạy local model:

```bash
python scripts/run_free_vi_benchmark.py --skip-local
```

## Model/Provider Đã Hỗ Trợ

| Provider | Model | Key | Ghi chú |
| --- | --- | --- | --- |
| `openai` | `gpt-4o-mini-transcribe` | `OPENAI_API_KEY` | API baseline hiện đang tốt nhất. |
| `groq` | `whisper-large-v3-turbo` | `GROQ_API_KEY` | Hosted Whisper nhanh, kết quả gần OpenAI. |
| `deepgram` | `nova-3` | `DEEPGRAM_API_KEY` | Production ASR API, đã benchmark. |
| `gemini` | `gemini-2.5-flash` | `GEMINI_API_KEY` | Đã tích hợp, đã có kết quả Studio 300. |
| `elevenlabs` | `scribe_v2` | `ELEVENLABS_API_KEY` | Đã tích hợp, chờ key. |
| `azure` | `azure-short-audio` | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | Đã tích hợp, chờ key. |
| `local-whisper` | `vinai/PhoWhisper-small` | none | Local/free Vietnamese baseline. |
| `local-whisper` | `openai/whisper-small` | none | Local/free Whisper baseline. |

Ví dụ chạy từng provider:

```bash
python scripts/run_asr_evaluation.py --provider openai --model gpt-4o-mini-transcribe --limit 300 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs/asr_eval_openai_new.csv
python scripts/run_asr_evaluation.py --provider groq --model whisper-large-v3-turbo --limit 300 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs/asr_eval_groq_whisper_large_v3_turbo.csv
python scripts/run_asr_evaluation.py --provider deepgram --model nova-3 --language vi --limit 300 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs/asr_eval_deepgram_nova3.csv
python scripts/run_asr_evaluation.py --provider gemini --model gemini-2.5-flash --language Vietnamese --limit 300 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs/asr_eval_gemini_2_5_flash.csv
python scripts/run_asr_evaluation.py --provider elevenlabs --model scribe_v2 --language vie --only-ground-truth --output-csv outputs/asr_eval_elevenlabs_scribe_v2.csv
python scripts/run_asr_evaluation.py --provider azure --model azure-short-audio --language vi-VN --only-ground-truth --output-csv outputs/asr_eval_azure_speech_vi_vn.csv
python scripts/run_asr_evaluation.py --provider local-whisper --model vinai/PhoWhisper-small --only-ground-truth --output-csv outputs/asr_eval_phowhisper_small.csv
```

## Quality Gate

Quality gate ban đầu:

- duration trong khoảng 1-20s
- SNR >= 20dB
- silence ratio <= 0.35
- clipping ratio <= 0.001
- absolute DC offset <= 0.02

Gate này dùng để ưu tiên review, không phải luật tuyệt đối. Clip fail gate vẫn có thể dùng nếu nghe tốt sau khi trim/normalize.

## Manual Decision

Trong `data/manual_eval_manifest.csv`, dùng:

- `usable_for_tts=yes`: sạch, single speaker, transcript khớp, có thể dùng training.
- `usable_for_tts=maybe`: cần trim/denoise/sửa transcript.
- `usable_for_tts=no`: loại khỏi dataset.

Các `reject_reason` nên dùng ngắn và nhất quán:

```text
music_overlap, multi_speaker, low_snr, clipping, bad_transcript,
too_short, too_long, non_speech, license_risk
```

## Output Chính

- `outputs/quality_report.csv`: audio metrics và quality gate.
- `outputs/asr_eval_*.csv`: transcript từ từng provider/model.
- `outputs/asr_eval_*_scored.csv`: WER/CER sau khi ghép ground truth.
- `outputs/evaluation_summary.md`: tổng hợp chất lượng audio và benchmark ASR.
- `outputs/benchmark_vi_models.md`: benchmark tiếng Việt mới nhất.
- `data/manual_eval_manifest.csv`: bảng điều phối review dataset.

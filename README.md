# TTS Audio Manual Evaluation

Project này dùng để đánh giá chất lượng audio/transcript cho dataset TTS trước khi mở rộng pipeline tự động thu thập dữ liệu từ internet, đặc biệt là YouTube.

Nguồn data mặc định:

```text
audio_samples/matched_audio
```

Các script mặc định xử lý 100 audio đầu tiên theo thứ tự tên file. Khi benchmark ASR, nên dùng `--only-ground-truth` để chỉ chạy những file đã có ground truth thủ công.

## Mục Tiêu

- Xác định tiêu chí audio/transcript đủ tốt để training TTS.
- Xây pipeline đánh giá chất lượng audio trước khi đưa vào dataset.
- So sánh ASR local open-source và API model trên cùng một tập sample.
- Tạo manifest để manual review: usable/reject, lỗi transcript, speaker, language, source.

## Kết Quả Hiện Tại

Dataset:

- 100 audio đầu từ `audio_samples/matched_audio`.
- 19 file ground truth trong `data/ground_truth`.
- 18 file ground truth có nội dung và được dùng để scoring.
- 1 file ground truth đang rỗng: `data/ground_truth/-aCDck13cRI_69.txt`.

Audio quality:

- PASS: 50/100 clips.
- REVIEW: 50/100 clips.
- Duration trung bình: 16.08s.
- Duration ngắn nhất/dài nhất: 3.24s / 30.00s.
- SNR trung bình: 46.13 dB.

ASR benchmark:

| Model | Provider | Status | GT matched | WER avg | CER avg |
| --- | --- | --- | ---: | ---: | ---: |
| `gpt-4o-mini-transcribe` | OpenAI | existing API result, rescored | 18 | 0.2238 | 0.1390 |
| `whisper-large-v3-turbo` | Groq | ok | 18 | 0.2565 | 0.1427 |
| `nova-3` | Deepgram | ok | 18 | 0.3620 | 0.2537 |
| `vinai/PhoWhisper-small` | local-whisper | previous 11-file run only; 18-file CPU run failed | 11 | 0.4317 | 0.2207 |
| `gemini-2.5-flash` | Gemini | failed: HTTP 429 quota/rate limit | 0 |  |  |
| `scribe_v2` | ElevenLabs | missing key | 0 |  |  |
| `azure-short-audio` | Azure Speech | missing key | 0 |  |  |

Current ranking:

1. `gpt-4o-mini-transcribe`: tốt nhất hiện tại trên subset 18 ground truth.
2. `whisper-large-v3-turbo`: rất gần OpenAI về CER, đáng mở rộng nếu còn free quota.
3. `nova-3`: chạy được nhưng kém hơn trên subset này.
4. `vinai/PhoWhisper-small`: baseline local/free hữu ích, nhưng cần môi trường local ổn định hơn.

Report chi tiết:

- `outputs/evaluation_summary.md`
- `outputs/benchmark_vi_models.md`
- `outputs/benchmark_free_vi_summary.csv`

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

1. Tạo manifest manual review:

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
python scripts/run_asr_evaluation.py --provider groq --model whisper-large-v3-turbo --only-ground-truth --output-csv outputs/asr_eval_groq_whisper_large_v3_turbo.csv
```

5. Chấm lại report ASR đã có mà không gọi API:

```bash
python scripts/score_existing_asr.py --input-csv outputs/asr_eval_openai.csv --output-csv outputs/asr_eval_openai_scored.csv
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
| `gemini` | `gemini-2.5-flash` | `GEMINI_API_KEY` | Đã tích hợp, hiện bị HTTP 429 free quota/rate limit. |
| `elevenlabs` | `scribe_v2` | `ELEVENLABS_API_KEY` | Đã tích hợp, chờ key. |
| `azure` | `azure-short-audio` | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | Đã tích hợp, chờ key. |
| `local-whisper` | `vinai/PhoWhisper-small` | none | Local/free Vietnamese baseline. |
| `local-whisper` | `openai/whisper-small` | none | Local/free Whisper baseline. |

Ví dụ chạy từng provider:

```bash
python scripts/run_asr_evaluation.py --provider openai --model gpt-4o-mini-transcribe --only-ground-truth --output-csv outputs/asr_eval_openai_new.csv
python scripts/run_asr_evaluation.py --provider groq --model whisper-large-v3-turbo --only-ground-truth --output-csv outputs/asr_eval_groq_whisper_large_v3_turbo.csv
python scripts/run_asr_evaluation.py --provider deepgram --model nova-3 --language vi --only-ground-truth --output-csv outputs/asr_eval_deepgram_nova3.csv
python scripts/run_asr_evaluation.py --provider gemini --model gemini-2.5-flash --language Vietnamese --only-ground-truth --output-csv outputs/asr_eval_gemini_2_5_flash.csv
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

# TTS Audio Benchmark & Data Review

Project này dùng để đánh giá chất lượng audio/transcript và benchmark ASR cho pipeline tạo dataset training TTS tiếng Việt.

Mục tiêu chính:

- So sánh ASR model/API trên dữ liệu thật.
- Chọn model transcript tốt nhất cho data pipeline TTS.
- Đánh giá nhanh chất lượng audio, transcript, empty output, WER/CER.
- Giữ checkpoint để không chạy lại audio đã benchmark.

## Current Verdict

- **Model nên chọn:** `openai:gpt-4o-mini-transcribe`
  - Studio full: **WER 0.1764**, **CER 0.0684**
  - Coverage: `2546/2546`
  - Empty output trên Studio 300: `0`
- **Model backup tốt nhất:** `groq:whisper-large-v3-turbo`
  - Studio full: **WER 0.2053**, **CER 0.0909**
  - Coverage: `2546/2546`
  - Empty output trên Studio 300: `0`
- **Chưa chọn làm model chính:** Deepgram, Gemini, iFLYTEK
  - Deepgram/Gemini có nhiều empty output hơn.
  - iFLYTEK hiện fail auth: `401 apikey not found`.

Report chính: [`Benchmark_final_result.md`](Benchmark_final_result.md)

## Dataset

| Dataset | Audio | Ground truth | Mục đích |
| --- | ---: | ---: | --- |
| `audio_samples/matched_audio` | 2277 | 32 | Dữ liệu internet/YouTube ban đầu |
| `audio_samples/studio` | 2548 | 2546 | Dữ liệu sạch chính để chọn model |

Khi scoring, annotation dạng `<...>` trong ground-truth được bỏ qua trước khi tính WER/CER.

## Benchmark Summary

### Studio Full

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | **0.1764** | **0.0684** | Best overall |
| 2 | Groq `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 | Best backup |
| 3 | Deepgram `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER ổn, CER kém hơn |
| 4 | Gemini `gemini-2.5-flash` | 1619/2546 | 0.2096 | 0.1094 | Chưa chạy full |

### Studio 300

| Rank | Model | Empty | WER | CER |
| ---: | --- | ---: | ---: | ---: |
| 1 | OpenAI `gpt-4o-mini-transcribe` | **0** | **0.1814** | **0.0668** |
| 2 | Groq `whisper-large-v3-turbo` | **0** | 0.2135 | 0.0851 |
| 3 | Deepgram `nova-3` | 21 | 0.2259 | 0.1286 |
| 4 | Gemini `gemini-2.5-flash` | 8 | 0.2346 | 0.1256 |

### matched_audio

| Rank | Model | Rows | WER | CER | Empty |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | OpenAI `gpt-4o-mini-transcribe` | 29 | **0.2044** | 0.1295 | 0 |
| 2 | Groq `whisper-large-v3-turbo` | 29 | 0.2234 | **0.1158** | 0 |
| 3 | Deepgram `nova-3` | 29 | 0.2982 | 0.2010 | 2 |
| 4 | Local `vinai/PhoWhisper-small` | 11 | 0.4317 | 0.2207 | 0 |

## Supported Providers

| Provider | Model | Env key |
| --- | --- | --- |
| `openai` | `gpt-4o-mini-transcribe` | `OPENAI_API_KEY` |
| `groq` | `whisper-large-v3-turbo` | `GROQ_API_KEY` |
| `deepgram` | `nova-3` | `DEEPGRAM_API_KEY` |
| `gemini` | `gemini-2.5-flash` | `GEMINI_API_KEY` |
| `iflytek` | `iat-niche` | `IFLYTEK_APP_ID`, `IFLYTEK_API_KEY`, `IFLYTEK_API_SECRET` |
| `elevenlabs` | `scribe_v2` | `ELEVENLABS_API_KEY` |
| `azure` | `azure-short-audio` | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` |
| `local-whisper` | `vinai/PhoWhisper-small` | none |

## Setup

```powershell
cd /d D:\TTS-audio
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and fill only the providers you want to test.

```env
OPENAI_API_KEY=
GROQ_API_KEY=
DEEPGRAM_API_KEY=
GEMINI_API_KEY=
IFLYTEK_APP_ID=
IFLYTEK_API_KEY=
IFLYTEK_API_SECRET=
IFLYTEK_LANGUAGE=vi
IFLYTEK_HOST_URL=wss://iat-niche-api.xfyun.cn/v2/iat
ASR_LANGUAGE=vi
```

`.env` is ignored by git.

## Common Commands

Run one provider on Studio 300:

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider openai --model gpt-4o-mini-transcribe --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vi --limit 300 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_300_asr_eval_openai_gpt_4o_mini.csv --output-jsonl outputs\studio_300_asr_eval_openai_gpt_4o_mini.jsonl
```

Run iFLYTEK after fixing key/service:

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider iflytek --model iat-niche --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vi --limit 1200 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_1200_asr_eval_iflytek_iat_niche.csv --output-jsonl outputs\studio_1200_asr_eval_iflytek_iat_niche.jsonl
```

Regenerate Studio 300 summary from saved outputs:

```powershell
python scripts\generate_studio_300_benchmark_summary.py
```

Score an existing ASR CSV without calling API:

```powershell
python scripts\score_existing_asr.py --input-csv outputs\asr_eval_openai.csv --output-csv outputs\asr_eval_openai_scored.csv --ground-truth data\ground_truth
```

## Project Structure

```text
Benchmark_final_result.md                 final benchmark report
configs/                                  benchmark/provider configs
data/ground_truth/                        manual GT for matched_audio
data/ground_truth_studio/                 GT for studio data
docs/                                     notes about data quality / ASR protocol
outputs/                                  generated reports and benchmark outputs
scripts/run_asr_evaluation.py             main ASR benchmark runner
scripts/score_existing_asr.py             rescore saved ASR outputs
scripts/generate_studio_300_benchmark_summary.py
src/tts_data_pipeline/                    core package
```

## Key Artifacts

- `Benchmark_final_result.md`
- `outputs/studio_full_benchmark_checkpoint_state.md`
- `outputs/studio_300_benchmark_summary.md`
- `outputs/initial_audio_samples_evaluation.md`
- `outputs/studio_1200_iflytek_evaluation_result.md`

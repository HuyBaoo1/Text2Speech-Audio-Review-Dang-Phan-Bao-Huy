# TTS Audio Benchmark & Data Review

Project này dùng để đánh giá chất lượng audio/transcript và benchmark ASR cho pipeline tạo dataset training TTS tiếng Việt.

## Mục tiêu

- So sánh ASR model/API trên dữ liệu thật.
- Chọn model transcript tốt nhất cho data pipeline TTS.
- Đánh giá nhanh WER, CER, empty output, lỗi API.
- Giữ checkpoint/cache để không chạy lại audio đã benchmark.

## Current Verdict

- **Model nên chọn:** OpenAI `gpt-4o-mini-transcribe`
  - Studio full: **WER 0.1764**, **CER 0.0684**
  - Coverage: `2546/2546`
  - Empty output trên Studio 300: `0`

- **Model backup tốt nhất:** Groq `whisper-large-v3-turbo`
  - Studio full: **WER 0.2053**, **CER 0.0909**
  - Coverage: `2546/2546`
  - Empty output trên Studio 300: `0`

- **Chưa nên chọn làm model chính:**
  - Deepgram: WER gần Groq nhưng CER kém hơn.
  - Gemini: kết quả ổn nhưng chưa chạy đủ full studio.
  - ElevenLabs: chất lượng rất tốt trên 980 file đã score, nhưng hết quota free trước khi chạy full.
  - Azure: WER cao hơn và lỗi API nhiều trong full run.
  - iFLYTEK: chưa benchmark được vì lỗi auth `401 apikey not found`.

Report chính: [`Benchmark_final_result.md`](Benchmark_final_result.md)

## Dataset

| Dataset | Audio | Ground truth | Mục đích |
| --- | ---: | ---: | --- |
| `audio_samples/matched_audio` | 2277 | 32 | Dữ liệu internet/YouTube ban đầu |
| `audio_samples/studio` | 2548 | 2546 | Dữ liệu sạch chính để chọn model |

Ghi chú: khi scoring, annotation dạng `<...>` trong ground-truth được bỏ qua trước khi tính WER/CER.

## Benchmark Summary

### Studio Full

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 980/2546 (out of quota) | **0.1179** | **0.0398** | Best partial |
| 2 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | **0.1764** | **0.0684** | Best overall |
| 3 | Groq `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 | Best backup |
| 4 | Deepgram `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER ổn, CER kém hơn |
| 5 | Gemini `gemini-2.5-flash` | 1619/2546 | 0.2096 | 0.1094 | Chưa chạy full |
| 6 | Azure `azure-short-audio` | 1632/2546 | 0.2361 | 0.1011 | Nhiều lỗi API |

### ElevenLabs Detail

| Metric | Value |
| --- | ---: |
| Model | `scribe_v2` |
| Scored rows | 980 |
| Current-key quota errors | 193 |
| Remaining rows not re-run after quota stop | 1373 |
| Empty scored hypotheses | 0 |
| WER mean | 0.1179 |
| CER mean | 0.0398 |

Kết luận ngắn: ElevenLabs cho chất lượng transcript rất mạnh trên 980 file đã score, tốt hơn OpenAI về WER/CER trong phần partial này.



## Supported Providers

| Provider | Model | Env key |
| --- | --- | --- |
| `openai` | `gpt-4o-mini-transcribe` | `OPENAI_API_KEY` |
| `groq` | `whisper-large-v3-turbo` | `GROQ_API_KEY` |
| `deepgram` | `nova-3` | `DEEPGRAM_API_KEY` |
| `gemini` | `gemini-2.5-flash` | `GEMINI_API_KEY` |
| `azure` | `azure-short-audio` | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` |
| `elevenlabs` | `scribe_v2` | `ELEVENLABS_API_KEY` |
| `iflytek` | `iat-niche` | `IFLYTEK_APP_ID`, `IFLYTEK_API_KEY`, `IFLYTEK_API_SECRET` |
| `local-whisper` | `vinai/PhoWhisper-small` | none |


## Project Structure

```text
Benchmark_final_result.md                         final benchmark report
configs/                                          benchmark/provider configs
data/ground_truth/                                manual GT for matched_audio
data/ground_truth_studio/                         GT for studio data
docs/                                             notes about data quality / ASR protocol
outputs/                                          generated reports and benchmark outputs
scripts/run_asr_evaluation.py                     main ASR benchmark runner
scripts/score_existing_asr.py                     rescore saved ASR outputs
scripts/generate_studio_300_benchmark_summary.py  summary generator
src/tts_data_pipeline/                            core package
```

## Final Recommendation

- Dùng **OpenAI `gpt-4o-mini-transcribe`** để tạo transcript chính.
- Dùng **Groq `whisper-large-v3-turbo`** làm backup hoặc lựa chọn tiết kiệm hơn.
- ElevenLabs `scribe_v2` rất đáng test tiếp bằng paid/quota cao hơn vì đang có WER/CER tốt nhất trên 980 file đã score.
- Chưa dùng Azure làm main pipeline cho tới khi xử lý được lỗi API và retry/backoff.
- Chưa benchmark iFLYTEK tiếp cho tới khi key có quyền đúng.
- Trước khi đưa transcript vào dataset TTS, luôn filter:
  - empty output
  - WER/CER cao bất thường
  - audio nhiều silence/noise/music
  - transcript có annotation hoặc text không phải lời thoại

# TTS Audio Benchmark & Data Review

Project này dùng để đánh giá chất lượng audio/transcript và benchmark ASR cho pipeline tạo dataset training TTS tiếng Việt.

## Mục tiêu

- So sánh ASR model/API trên dữ liệu thật.
- Chọn model transcript tốt nhất cho data pipeline TTS.
- Đánh giá nhanh WER, CER, empty output, lỗi API.
- Giữ checkpoint/cache để không chạy lại audio đã benchmark.

## Current Verdict

- **Model nên chọn:** ElevenLabs `scribe_v2`, Gemini `gemini-3.1-flash-lite`, OpenAI `gpt-4o-mini-transcribe`

- **Model backup tốt nhất:** Gemini `gemini-3.5-flash`, Groq `whisper-large-v3-turbo`

- **Chưa nên chọn làm model chính:**
  - Deepgram: WER gần Groq nhưng CER kém hơn.
  - Gemini `gemini-2.5-flash`: chạy full được nhưng nhiều empty output.
  - Azure: WER cao hơn và lỗi API nhiều trong full run.
  - iFLYTEK: chưa benchmark được vì lỗi auth `401 apikey not found`.


## Dataset

| Dataset | Audio | Ground truth | Mục đích |
| --- | ---: | ---: | --- |
| `audio_samples/matched_audio` | 2277 | 32 | Dữ liệu internet/YouTube ban đầu |
| `audio_samples/studio` | 2548 | 2546 | Dữ liệu sạch chính để chọn model |

Ghi chú: khi scoring, annotation dạng `<...>` trong ground-truth được bỏ qua trước khi tính WER/CER.

## Benchmark Summary


| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 2577/2577 | **0.1240** | **0.0457** | Tốt nhất trên tập gộp |
| 2 | Gemini `gemini-3.1-flash-lite` | 2577/2577 | 0.1702 | 0.0662 | Gemini ổn định nhất |
| 3 | OpenAI `gpt-4o-mini-transcribe` | 2577/2577 | 0.1766 | 0.0690 | Baseline ổn định |
| 4 | Groq `whisper-large-v3` | 2577/2577 | 0.2029 | 0.0865 | Groq tốt nhất |
| 5 | Groq `whisper-large-v3-turbo` | 2577/2577 | 0.2055 | 0.0912 | Nhanh, nhưng thấp hơn V3 |
| 6 | Deepgram `nova-3` | 2577/2577 | 0.2072 | 0.1114 | Có 123 empty output |
| 7 | Gemini `gemini-2.5-flash` | 2577/2577 | 0.2160 | 0.1119 | Có 54 empty output |
| 8 | Azure `azure-short-audio` | 1659/2577 | 0.2365 | 0.1016 | Partial, 918 lỗi API |
| - | Gemini `gemini-2.5-pro` | 120/2577 | 0.1728 | 0.0682 | Partial |
| - | Gemini `gemini-3.5-flash` | 2558/2577 | 0.1637 | 0.0638 | Partial, 19 lỗi API |

Kết luận ngắn:

- Chọn `scribe_v2` nếu ưu tiên chất lượng transcript.
- Chọn `gemini-3.1-flash-lite` hoặc `gpt-4o-mini-transcribe` khi cần lựa chọn ổn định.
- Trong Groq, chọn `whisper-large-v3`; Turbo phù hợp khi ưu tiên tốc độ hơn một chút về chất lượng.
- Không dùng các model partial/empty-output làm nguồn transcript chính trước khi xử lý lỗi.

### ElevenLabs Detail

| Metric | Value |
| --- | ---: |
| Model | `scribe_v2` |
| Scored rows | 2544 |
| Error rows | 0 |
| Ground-truth annotation-only rows skipped | 2 |
| Empty scored hypotheses | 0 |
| WER mean | 0.1233 |
| CER mean | 0.0450 |

Studio 300 check:

| Metric | Value |
| --- | ---: |
| Selected rows | 300 |
| Scored rows | 300 |
| Error rows | 0 |
| Empty scored hypotheses | 0 |
| WER mean | 0.1316 |
| CER mean | 0.0431 |

Kết luận ngắn: ElevenLabs cho chất lượng transcript tốt nhất hiện tại trên studio, thấp hơn OpenAI rõ rệt về WER/CER và không tạo empty output trên phần scored.



## Supported Providers

| Provider | Model | Env key |
| --- | --- | --- |
| `openai` | `gpt-4o-mini-transcribe` | `OPENAI_API_KEY` |
| `openai-realtime` | `gpt-realtime-2` | `OPENAI_API_KEY` |
| `groq` | `whisper-large-v3-turbo` | `GROQ_API_KEY` |
| `deepgram` | `nova-3` | `DEEPGRAM_API_KEY` |
| `gemini` | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-3.5-flash`, `gemini-3.1-flash-lite` | `GEMINI_API_KEY` |
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
- **Best overall:** ElevenLabs `scribe_v2` vẫn là model nên ưu tiên nếu quota/chi phí cho phép: WER/CER thấp nhất, không có empty output trên phần scored.
- **Best production Gemini:** Gemini `gemini-3.1-flash-lite` là lựa chọn Gemini đáng dùng nhất hiện tại: gần full coverage, 0 API error, WER/CER tốt hơn OpenAI baseline.
- **Best Gemini by raw score:** Gemini `gemini-3.5-flash` có WER/CER tốt hơn `3.1-flash-lite`, nhưng chưa nên chọn làm main nếu chưa có retry/backoff vì còn 19 lỗi network/API.
- **Stable baseline:** OpenAI `gpt-4o-mini-transcribe` vẫn nên giữ làm baseline đối chứng vì full coverage và vận hành ổn định.
- **Backup tiết kiệm/không phụ thuộc Gemini:** Groq `whisper-large-v3-turbo` là lựa chọn backup hợp lý dù WER/CER thấp hơn nhóm top.
- **Không khuyến nghị làm main hiện tại:** Azure cần xử lý lỗi API/retry; Gemini `2.5-flash` có nhiều empty output; Gemini `2.5-pro` quá chậm và mới có partial result; Deepgram CER kém hơn Groq; iFLYTEK chưa benchmark được do lỗi auth.
- Trước khi đưa transcript vào dataset TTS, luôn filter:
  - empty output
  - WER/CER cao bất thường
  - audio nhiều silence/noise/music
  - transcript có annotation hoặc text không phải lời thoại

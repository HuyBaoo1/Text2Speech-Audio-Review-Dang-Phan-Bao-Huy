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

### Studio Full

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 2544/2546 | **0.1233** | **0.0450** | Best overall ASR quality |
| 2 | Gemini `gemini-3.5-flash` | 2525/2546 | **0.1637** | **0.0636** | Best Gemini by score, còn 19 network/API errors |
| 3 | Gemini `gemini-3.1-flash-lite` | 2544/2546 | **0.1702** | **0.0660** | Best stable Gemini, 0 API error |
| 4 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | 0.1764 | 0.0684 | Stable full baseline |
| - | Gemini `gemini-2.5-pro` | 89/90 | 0.1745 | 0.0638 | Partial only, quá chậm để rank full |
| 5 | Groq `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 | Best backup không dùng Gemini |
| 6 | Deepgram `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER ổn, CER kém hơn |
| 7 | Gemini `gemini-2.5-flash` | 2546/2546 | 0.2161 | 0.1119 | Full, nhiều empty hơn |
| 8 | Azure `azure-short-audio` | 1632/2546 | 0.2361 | 0.1011 | Nhiều lỗi API |

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

### Gemini Model Benchmark

Studio results:

| Model | Scope | Scored | Empty | WER | CER | Ghi chú |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `gemini-3.5-flash` | Studio full | 2525/2546 | 0 | **0.1637** | **0.0636** | Best Gemini by score, còn 19 network/API errors |
| `gemini-3.1-flash-lite` | Studio full | 2544/2546 | 0 | 0.1702 | 0.0660 | Best stable Gemini, 0 API error |
| `gemini-2.5-pro` | Studio partial | 89/90 | 0 | 0.1745 | 0.0638 | Quá chậm, dừng checkpoint |
| `gemini-2.5-flash` | Studio full | 2546/2546 | 53 | 0.2161 | 0.1119 | Chạy full nhưng nhiều empty |

matched_audio results:

| Model | Rows | Empty | WER | CER |
| --- | ---: | ---: | ---: | ---: |
| `gemini-3.5-flash` | 31 | 0 | **0.1636** | 0.0806 |
| `gemini-2.5-pro` | 31 | 0 | 0.1680 | 0.0809 |
| `gemini-3.1-flash-lite` | 31 | 0 | 0.1738 | **0.0794** |
| `gemini-2.5-flash` | 31 | 1 | 0.2057 | 0.1149 |

Skipped Gemini aliases:

| Requested model | Status | Note |
| --- | --- | --- |
| `gemini-3` | Skipped | API returned 404: model not found for `generateContent` |
| `gemini-3.1-pro` | Skipped | API returned 404: model not found for `generateContent` |

Kết luận ngắn: trong nhóm Gemini, `gemini-3.5-flash` có WER/CER tốt nhất trên full studio nhưng còn 19 lỗi network/API cần retry nếu dùng production. `gemini-3.1-flash-lite` là lựa chọn Gemini ổn định nhất hiện tại: full studio, 0 API error, WER/CER tốt hơn OpenAI baseline. `gemini-2.5-pro` chất lượng ổn trên mẫu nhỏ nhưng quá chậm để rank full. `gemini-2.5-flash` chạy full được nhưng WER/CER và empty output kém hơn các model mới.



## Supported Providers

| Provider | Model | Env key |
| --- | --- | --- |
| `openai` | `gpt-4o-mini-transcribe` | `OPENAI_API_KEY` |
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

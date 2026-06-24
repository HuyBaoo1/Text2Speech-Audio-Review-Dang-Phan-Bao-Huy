# TTS Audio Benchmark & Data Review

Project này dùng để đánh giá chất lượng audio/transcript và benchmark ASR cho pipeline tạo dataset training TTS tiếng Việt.

## Mục tiêu

- So sánh ASR model/API trên dữ liệu thật.
- Chọn model transcript tốt nhất cho data pipeline TTS.
- Đánh giá nhanh WER, CER, empty output, lỗi API.
- Giữ checkpoint/cache để không chạy lại audio đã benchmark.

## Current Verdict

- **Model nên chọn:** OpenAI `gpt-4o-mini-transcribe`, ElevenLabs `scribe_v2`

- **Model backup tốt nhất:** Groq `whisper-large-v3-turbo`

- **Chưa nên chọn làm model chính:**
  - Deepgram: WER gần Groq nhưng CER kém hơn.
  - Gemini: các model Flash/Pro đã test, chất lượng nhìn chung kém ElevenLabs/OpenAI trên studio.
  - Azure: WER cao hơn và lỗi API nhiều trong full run.
  - iFLYTEK: chưa benchmark được vì lỗi auth `401 apikey not found`.


## Dataset

| Dataset | Audio | Ground truth | Mục đích |
| --- | ---: | ---: | --- |
| `audio_samples/matched_audio` | 2277 | 35 | Dữ liệu internet/YouTube có noise và tạp âm |
| `audio_samples/studio` | 2548 | 2546 | Dữ liệu sạch chính để chọn model |

Ghi chú: khi scoring, annotation dạng `<...>` trong ground-truth được bỏ qua trước khi tính WER/CER.

## Benchmark Summary


### matched_audio Benchmark — noisy / tạp âm

Dữ liệu internet/YouTube có noise và tạp âm; target hiện tại là 35 audio có ground truth.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | Gemini `gemini-3.5-flash` | 35/35 | 0.1628 | 0.0793 | Tốt nhất trên tập này |
| 2 | Gemini `gemini-2.5-pro` | 35/35 | 0.1646 | 0.0788 | Đủ coverage, có thể so sánh trực tiếp |
| 3 | Gemini `gemini-3.1-flash-lite` | 35/35 | 0.1718 | 0.0778 | Đủ coverage, có thể so sánh trực tiếp |
| 4 | Gemini `gemini-3-flash-preview` | 35/35 | 0.1789 | 0.0888 | Đủ coverage, có thể so sánh trực tiếp |
| 5 | ElevenLabs `scribe_v2` | 35/35 | 0.1790 | 0.0935 | Đủ coverage, có thể so sánh trực tiếp |
| 6 | OpenAI `gpt-4o-mini-transcribe` | 35/35 | 0.1933 | 0.1193 | Đủ coverage, có thể so sánh trực tiếp |
| 7 | Groq `whisper-large-v3-turbo` | 35/35 | 0.2195 | 0.1157 | Đủ coverage, có thể so sánh trực tiếp |
| 8 | Groq `whisper-large-v3` | 35/35 | 0.2258 | 0.1091 | Đủ coverage, có thể so sánh trực tiếp |
| 9 | Gemini `gemini-2.5-flash` | 35/35 | 0.2483 | 0.1631 | Đủ coverage, có thể so sánh trực tiếp; 3 output rỗng |
| 10 | Deepgram `nova-3` | 35/35 | 0.2804 | 0.1850 | Đủ coverage, có thể so sánh trực tiếp; 2 output rỗng |
| - | Azure `azure-short-audio` | 25/35 | 0.2587 | 0.1323 | Partial; thiếu 10 mẫu, 10 API errors |
| - | Gemini `gemini-2.5-flash-lite` | 0/35 | - | - | Partial; thiếu 35 mẫu |
| - | Gemini `gemini-3.1-pro-preview` | 31/35 | 0.1465 | 0.0681 | Partial; thiếu 4 mẫu |
| - | OpenAI `gpt-4o-transcribe` | 31/35 | 0.5210 | 0.4633 | Partial; thiếu 4 mẫu, 4 API errors |
| - | OpenAI `gpt-realtime-2` | 31/35 | 0.3904 | 0.2911 | Partial; thiếu 4 mẫu, 4 API errors |

Kết luận ngắn: Gemini `gemini-3.5-flash` có WER thấp nhất trong các model hoàn tất trên tập này.


### Studio Benchmark — clean

Dữ liệu thu studio sạch; target hiện tại là 2546 audio có ground truth.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 2546/2546 | 0.1233 | 0.0450 | Tốt nhất trên tập này |
| 2 | Gemini `gemini-3.5-flash` | 2546/2546 | 0.1650 | 0.0645 | Gemini tốt nhất đã chạy full; cân bằng tốt giữa chất lượng và vận hành|
| 3 | Gemini `gemini-3.1-flash-lite` | 2546/2546 | 0.1702 | 0.0660 | Ổn định, chất lượng sát Gemini 3.5 Flash; phù hợp khi ưu tiên model nhẹ hơn |
| 4 | Gemini `gemini-2.5-pro` | 2546/2546 | 0.1727 | 0.0705 | Chất lượng tốt nhưng throughput chậm; chỉ nên dùng khi không gấp về thời gian |
| 5 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | 0.1764 | 0.0684 | Baseline full-coverage đáng tin cậy, chất lượng tốt và dễ chọn cho production |
| 6 | Groq `whisper-large-v3` | 2546/2546 | 0.2026 | 0.0861 | Lựa chọn Groq tốt nhất về độ chính xác |
| 7 | Groq `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 |Chất lượng rất gần V3; phù hợp hơn khi ưu tiên tốc độ/chi phí |
| 8 | Deepgram `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER ổn nhưng CER cao và có nhiều output rỗng; cần hậu kiểm; 121 output rỗng |
| 9 | Gemini `gemini-2.5-flash` | 2546/2546 | 0.2161 | 0.1119 | Đủ coverage, có thể so sánh trực tiếp; 53 output rỗng |
| 10 | Qwen3-ASR `1.7B` | 2546/2546 | 0.2165 | 0.0809 |Tốt nhất trong hai bản Qwen; CER khá tốt, không có output rỗng |
| 11 | Qwen3-ASR `0.6B` | 2546/2546 | 0.2266 | 0.0900 | Bản gọn hơn nhưng chất lượng giảm rõ so với 1.7B |
| - | Azure `azure-short-audio` | 1833/2546 | 0.2398 | 0.1039 | Partial; thiếu 713 mẫu, 713 API errors |
| - | Gemini `gemini-2.5-flash-lite` | 0/2546 | - | - | Partial; thiếu 2546 mẫu |
| - | Gemini `gemini-3-flash-preview` | 1269/2546 | 0.1578 | 0.0588 | Partial; thiếu 1277 mẫu, 3 API errors |
| - | Gemini `gemini-3.1-pro-preview` | 0/2546 | - | - | Partial; thiếu 2546 mẫu |
| - | OpenAI `gpt-4o-transcribe` | 883/2546 | 0.1750 | 0.0649 | Partial; thiếu 1663 mẫu, 14 API errors |
| - | OpenAI `gpt-realtime-2` | 453/2546 | 0.2151 | 0.0931 | Partial; thiếu 2093 mẫu, 2093 API errors |

Kết luận ngắn: ElevenLabs `scribe_v2` có WER thấp nhất trong các model hoàn tất trên tập này.

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
| `gemini-3.5-flash` | Studio 300 | 298/300 | 0 | **0.1670** | **0.0618** | 2 timeout errors |
| `gemini-2.5-pro` | Studio full | 2544/2546 | 0 | 0.1727 | 0.0705 | Hoàn tất; 2 ground-truth annotation-only không chấm WER/CER |
| `gemini-3.1-flash-lite` | Studio 300 | 300/300 | 0 | 0.1757 | 0.0652 | Lite tốt, ổn định |
| `gemini-2.5-flash` | Studio full | 2546/2546 | 53 | 0.2161 | 0.1119 | Chạy full nhưng nhiều empty |

matched_audio results:

| Model | Rows | Empty | WER | CER |
| --- | ---: | ---: | ---: | ---: |
| `gemini-3.5-flash` | 35 | 0 | **0.1628** | 0.0793 |
| `gemini-2.5-pro` | 35 | 0 | 0.1646 | 0.0788 |
| `gemini-3.1-flash-lite` | 35 | 0 | 0.1718 | **0.0778** |
| `gemini-2.5-flash` | 35 | 3 | 0.2483 | 0.1631 |

Skipped Gemini aliases:

| Requested model | Status | Note |
| --- | --- | --- |
| `gemini-3` | Skipped | API returned 404: model not found for `generateContent` |
| `gemini-3.1-pro` | Skipped | API returned 404: model not found for `generateContent` |

Kết luận ngắn: trong nhóm Gemini, `gemini-3.5-flash` dẫn đầu trên matched_audio; `gemini-2.5-pro` đã hoàn tất Studio full với WER 0.1727/CER 0.0705, nhưng chậm hơn đáng kể. `gemini-2.5-flash` chạy full được nhưng WER/CER và empty output kém hơn các model mới.



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

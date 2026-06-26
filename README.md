# TTS Audio Benchmark & Data Review

Project này dùng để đánh giá chất lượng audio/transcript và benchmark ASR cho pipeline tạo dataset training TTS tiếng Việt.

## Mục tiêu

- So sánh ASR model/API trên dữ liệu thật.
- Chọn model transcript tốt nhất cho data pipeline TTS.
- Đánh giá nhanh WER, CER, empty output, lỗi API.
- Giữ checkpoint/cache để không chạy lại audio đã benchmark.

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
| 1 | Gemini `gemini-3.5-flash` | 35/35 | 0.1628 | 0.0793 | Gemini tốt nhất trên audio nhiễu |
| 2 | Gemini `gemini-2.5-pro` | 35/35 | 0.1646 | 0.0788 | Chất lượng sát Gemini 3.5 Flash |
| 3 | Gemini `gemini-3.1-flash-lite` | 35/35 | 0.1718 | 0.0778 | Ổn định, CER tốt nhất nhóm Gemini full |
| 4 | Gemini `gemini-3-flash-preview` | 35/35 | 0.1789 | 0.0888 | Kết quả mạnh, ngay sau nhóm Gemini dẫn đầu |
| 5 | ElevenLabs `scribe_v2` | 35/35 | 0.1790 | 0.0935 | Chất lượng cao trên audio nhiễu |
| 6 | OpenAI `gpt-4o-mini-transcribe` | 35/35 | 0.1933 | 0.1193 | Baseline ổn định, chất lượng khá |
| 7 | Groq `whisper-large-v3-turbo` | 35/35 | 0.2195 | 0.1157 | Lựa chọn Groq tốt hơn trên audio nhiễu |
| 8 | Groq `whisper-large-v3` | 35/35 | 0.2258 | 0.1091 | CER tốt hơn Turbo, nhưng WER kém hơn trên noise |
| 9 | Gemini `gemini-2.5-flash` | 35/35 | 0.2483 | 0.1631 | Sai nhiều hơn và có output rỗng; 3 output rỗng |
| 10 | Deepgram `nova-3` | 35/35 | 0.2804 | 0.1850 | Nhiều lỗi hơn và có output rỗng; 2 output rỗng |
| - | Azure `azure-short-audio` | 25/35 | 0.2587 | 0.1323 | Bị quota/API error, chưa đủ dữ liệu; thiếu 10 mẫu, 10 API errors |
| - | Gemini `gemini-2.5-flash-lite` | 0/35 | - | - | Chưa chạy benchmark; thiếu 35 mẫu |
| - | Gemini `gemini-3.1-pro-preview` | 31/35 | 0.1465 | 0.0681 | Điểm tạm thời rất tốt, chưa đủ coverage; thiếu 4 mẫu |
| - | OpenAI `gpt-4o-transcribe` | 31/35 | 0.5210 | 0.4633 | Chưa đủ coverage do quota; thiếu 4 mẫu, 4 API errors |
| - | OpenAI `gpt-realtime-2` | 31/35 | 0.3904 | 0.2911 | Chưa đủ coverage do quota; thiếu 4 mẫu, 4 API errors |

Kết luận ngắn: Gemini `gemini-3.5-flash` có WER thấp nhất trong các model hoàn tất trên tập này.


### Studio Benchmark — clean

Dữ liệu thu studio sạch; target hiện tại là 2546 audio có ground truth.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 2546/2546 | 0.1233 | 0.0450 | Tốt nhất toàn bảng, ưu tiên độ chính xác |
| 2 | Gemini `gemini-3.5-flash` | 2546/2546 | 0.1650 | 0.0645 | Gemini tốt nhất đã chạy full |
| 3 | Gemini `gemini-3.1-flash-lite` | 2546/2546 | 0.1702 | 0.0660 | Ổn định, sát Gemini 3.5 Flash |
| 4 | Gemini `gemini-3-flash-preview` | 2545/2546 | 0.1714 | 0.0702 | Điểm tạm thời rất mạnh, chờ timeout cuối; thiếu 1 mẫu, 1 API errors |
| 5 | Gemini `gemini-3-flash-preview` | 2546/2546 | 0.1789 | 0.0888 | chất lượng rất mạnh, đứng sau top 3 Gemini; tốt hơn Gemini 2.5 Pro và OpenAI mini trên WER |
| 6 | Gemini `gemini-2.5-pro` | 2546/2546 | 0.1727 | 0.0705 | Chất lượng tốt nhưng throughput chậm |
| 7 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | 0.1764 | 0.0684 | Baseline production ổn định |
| 8 | Groq `whisper-large-v3` | 2546/2546 | 0.2026 | 0.0861 | Groq chính xác nhất trên Studio |
| 9 | Groq `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 | Gần V3, hợp khi ưu tiên tốc độ |
| 10 | Deepgram `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER ổn nhưng CER cao và nhiều output rỗng; 121 output rỗng |
| 11 | Gemini `gemini-2.5-flash` | 2546/2546 | 0.2161 | 0.1119 | Chạy full nhưng nhiều output rỗng; 53 output rỗng |
| 12 | Qwen3-ASR `1.7B` | 2546/2546 | 0.2165 | 0.0809 | Tốt nhất trong hai bản Qwen, không output rỗng |
| 13 | Qwen3-ASR `0.6B` | 2546/2546 | 0.2266 | 0.0900 | Nhẹ hơn nhưng kém bản 1.7B |
| 14 | Azure `azure-short-audio` | 1914/2546 | 0.2408 | 0.1047 | Bị quota/API error, chưa đủ dữ liệu; thiếu 632 mẫu, 632 API errors |
| - | Gemini `gemini-2.5-flash-lite` | 0/2546 | - | - | Chưa chạy benchmark; thiếu 2546 mẫu |
| - | Gemini `gemini-3.1-pro-preview` | 0/2546 | - | - | Chưa chạy benchmark; thiếu 2546 mẫu |

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


Kết luận ngắn: ElevenLabs cho chất lượng transcript tốt nhất hiện tại trên studio, thấp hơn OpenAI rõ rệt về WER/CER và không tạo empty output trên phần scored.


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

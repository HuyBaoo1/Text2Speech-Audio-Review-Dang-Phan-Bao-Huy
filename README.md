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
| 1 | Gemini `gemini-3.1-pro-preview` | 35/35 | 0.1460 | 0.0674 | Tốt nhất trên audio nhiễu trong lượt chạy này |
| 2 | Gemini `gemini-3.5-flash` | 35/35 | 0.1628 | 0.0793 | Gemini full coverage rất mạnh trên audio nhiễu |
| 3 | Gemini `gemini-2.5-pro` | 35/35 | 0.1646 | 0.0788 | Chất lượng sát Gemini 3.5 Flash |
| 4 | Gemini `gemini-3.1-flash-lite` | 35/35 | 0.1718 | 0.0778 | Ổn định, CER tốt nhất nhóm Gemini full cũ |
| 5 | Gemini `gemini-3-flash-preview` | 35/35 | 0.1789 | 0.0888 | Kết quả mạnh, ngay sau nhóm Gemini dẫn đầu |
| 6 | ElevenLabs `scribe_v2` | 35/35 | 0.1790 | 0.0935 | Chất lượng cao trên audio nhiễu |
| 7 | OpenAI `gpt-4o-mini-transcribe` | 35/35 | 0.1933 | 0.1193 | Baseline ổn định, chất lượng khá |
| 8 | Groq `whisper-large-v3-turbo` | 35/35 | 0.2195 | 0.1157 | Lựa chọn Groq tốt hơn trên audio nhiễu |
| 9 | Groq `whisper-large-v3` | 35/35 | 0.2258 | 0.1091 | CER tốt hơn Turbo, nhưng WER kém hơn trên noise |
| 10 | Gemini `gemini-2.5-flash` | 35/35 | 0.2483 | 0.1631 | Sai nhiều hơn và có output rỗng; 3 output rỗng |
| 11 | Deepgram `nova-3` | 35/35 | 0.2804 | 0.1850 | Nhiều lỗi hơn và có output rỗng; 2 output rỗng |
| 12 | Gemini `gemini-2.5-flash-lite` | 35/35 | 15.5338 | 16.6243 | Full coverage nhưng lỗi transcript rất nặng trên tập nhiễu; không khuyến nghị |
| - | Azure `azure-short-audio` | 25/35 | 0.2587 | 0.1323 | Bị quota/API error, chưa đủ dữ liệu; thiếu 10 mẫu, 10 API errors |
| - | OpenAI `gpt-realtime-2` | 31/35 | 0.3904 | 0.2911 | Chưa đủ coverage do quota; thiếu 4 mẫu, 4 API errors |
| - | OpenAI `gpt-4o-transcribe` | 31/35 | 0.5210 | 0.4633 | Chưa đủ coverage do quota; thiếu 4 mẫu, 4 API errors |

Kết luận ngắn: Gemini `gemini-3.1-pro-preview` có WER/CER thấp nhất trong các model hoàn tất trên tập này; Gemini `gemini-2.5-flash-lite` không phù hợp với audio nhiễu trong lượt test này.


### Studio Benchmark — clean

Dữ liệu thu studio sạch; target lượt này là 500 audio đầu tiên có ground truth. Rank trong bảng này chỉ dựa trên WER tăng dần, sau đó CER tăng dần; coverage/API errors chỉ dùng để tham chiếu độ hoàn tất.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 500/500 | 0.1285 | 0.0433 | Tốt nhất toàn bảng trên Studio 500 |
| 2 | Gemini `gemini-3.1-pro-preview` | 496/500 | 0.1578 | 0.0574 | Xếp hạng theo WER/CER hiện tại; còn 4 API errors, 0 output rỗng sau retry |
| 3 | Gemini `gemini-3.5-flash` | 500/500 | 0.1717 | 0.0638 | Gemini full coverage tốt nhất trên Studio 500 |
| 4 | Gemini `gemini-3-flash-preview` | 500/500 | 0.1755 | 0.0668 | Chất lượng mạnh, full coverage |
| 5 | Gemini `gemini-3.1-flash-lite` | 500/500 | 0.1810 | 0.0672 | Ổn định, sát nhóm Gemini dẫn đầu |
| 6 | Gemini `gemini-2.5-pro` | 500/500 | 0.1818 | 0.0746 | Chất lượng tốt nhưng throughput chậm |
| 7 | OpenAI `gpt-4o-mini-transcribe` | 500/500 | 0.1856 | 0.0688 | Baseline production ổn định |
| 8 | Gemini `gemini-2.5-flash-lite` | 500/500 | 0.1967 | 0.0955 | Full coverage, tốt hơn Groq Turbo về WER nhưng kém nhóm Gemini top |
| 9 | Groq `whisper-large-v3-turbo` | 500/500 | 0.2160 | 0.0901 | Hợp khi ưu tiên tốc độ/backup |
| 10 | Deepgram `nova-3` | 500/500 | 0.2275 | 0.1286 | CER cao và nhiều output rỗng; 34 output rỗng |
| 11 | Qwen3-ASR `1.7B` | 500/500 | 0.2354 | 0.0854 | Tốt nhất trong hai bản Qwen trên Studio 500 |
| 12 | Gemini `gemini-2.5-flash` | 500/500 | 0.2357 | 0.1254 | Nhiều output rỗng; 11 output rỗng |
| 13 | Qwen3-ASR `0.6B` | 500/500 | 0.2425 | 0.0937 | Nhẹ hơn nhưng kém bản 1.7B |
| 14 | Azure `azure-short-audio` | 500/500 | 0.2624 | 0.1163 | Full coverage trong tập 500 nhưng WER cao |

Kết luận ngắn: ElevenLabs `scribe_v2` có WER thấp nhất trên Studio 500. Theo WER/CER hiện tại sau retry, `gemini-3.1-pro-preview` đứng cao nhất trong nhóm Gemini; `gemini-2.5-flash-lite` xếp sau OpenAI baseline và trước Groq Turbo.

### Studio Full Folder Benchmark — clean

Dữ liệu thu studio sạch; bảng này chỉ gồm các model đã chạy đủ full folder `audio_samples/studio` với target 2546 audio có ground truth. Khi scoring, 2 dòng ground-truth chỉ còn annotation sau khi strip `<...>` được bỏ qua, nên số dòng scored là 2544.

| Rank | Model | Coverage | Scored | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | ElevenLabs `scribe_v2` | 2546/2546 | 2544 | 0.1233 | 0.0450 | Tốt nhất full studio |
| 2 | Gemini `gemini-3.5-flash` | 2546/2546 | 2544 | 0.1650 | 0.0645 | Gemini full-folder tốt nhất |
| 3 | Gemini `gemini-3.1-flash-lite` | 2546/2546 | 2544 | 0.1702 | 0.0660 | Ổn định, sát nhóm đầu Gemini |
| 4 | Gemini `gemini-3-flash-preview` | 2546/2546 | 2544 | 0.1715 | 0.0703 | Full coverage, chất lượng tốt |
| 5 | Gemini `gemini-2.5-pro` | 2546/2546 | 2544 | 0.1727 | 0.0705 | Chất lượng tốt nhưng throughput chậm |
| 6 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | 2544 | 0.1753 | 0.0649 | Baseline production ổn định |
| 7 | Gemini `gemini-2.5-flash-lite` | 2546/2546 | 2544 | 0.1895 | 0.1083 | Full folder sau retry, không output rỗng |
| 8 | Groq `whisper-large-v3-turbo` | 2546/2546 | 2544 | 0.2040 | 0.0868 | Backup hợp khi ưu tiên tốc độ |
| 9 | Deepgram `nova-3` | 2546/2546 | 2544 | 0.2047 | 0.1065 | WER gần Groq Turbo nhưng có 119 output rỗng |
| 10 | Gemini `gemini-2.5-flash` | 2546/2546 | 2544 | 0.2151 | 0.1096 | Nhiều output rỗng; 52 output rỗng |
| 11 | Qwen3-ASR `1.7B` | 2546/2546 | 2544 | 0.2165 | 0.0809 | Tốt nhất trong hai bản Qwen |
| 12 | Qwen3-ASR `0.6B` | 2546/2546 | 2544 | 0.2266 | 0.0900 | Nhẹ hơn nhưng kém bản 1.7B |

Kết luận ngắn: ElevenLabs `scribe_v2` vẫn đứng đầu trên full studio. Trong nhóm Gemini đã chạy full folder, `gemini-3.5-flash` có WER tốt nhất; `gemini-2.5-flash-lite` đã hoàn tất full folder nhưng kém hơn nhóm Gemini top.

### ElevenLabs Detail — full studio

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
| `gemini` | `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.5-pro`, `gemini-3-flash-preview`, `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, `gemini-3.5-flash` | `GEMINI_API_KEY` |
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
- **Best Gemini by raw score:** Gemini `gemini-3.1-pro-preview` đang tốt nhất trên matched_audio và đứng đầu nhóm Gemini trên Studio 500, nhưng Studio mới đạt 496/500 vì còn 4 API errors.
- **Best production Gemini full coverage:** Gemini `gemini-3.5-flash` là lựa chọn Gemini full-coverage tốt nhất trên cả Studio 500 và full studio; `gemini-3.1-flash-lite` vẫn ổn định nhưng kém hơn một chút.
- **Stable baseline:** OpenAI `gpt-4o-mini-transcribe` vẫn nên giữ làm baseline đối chứng vì full coverage và vận hành ổn định trên Studio 500.
- **Backup tiết kiệm/không phụ thuộc Gemini:** Groq `whisper-large-v3-turbo` là lựa chọn backup hợp lý dù WER/CER thấp hơn nhóm top.
- **Không khuyến nghị làm main hiện tại:** Gemini `2.5-flash-lite` fail nặng trên matched_audio dù ổn hơn trên Studio 500; Gemini `2.5-flash` có nhiều empty output; Azure/`3.1-pro-preview` cần retry/backoff ổn định hơn; Deepgram CER cao; iFLYTEK chưa benchmark được do lỗi auth.
- Trước khi đưa transcript vào dataset TTS, luôn filter:
  - empty output
  - WER/CER cao bất thường
  - audio nhiều silence/noise/music
  - transcript có annotation hoặc text không phải lời thoại

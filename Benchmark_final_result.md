# Benchmark Final Result

## Kết Luận Nhanh

- **Model nên chọn:** `openai:gpt-4o-mini-transcribe`
  - Tốt nhất trên cả `matched_audio` và `studio`.
  - Studio full: **WER 0.1764**, **CER 0.0684**, `2546/2546` file thành công.
- **Model backup/free-quota tốt nhất:** `groq:whisper-large-v3-turbo`
  - Studio full: **WER 0.2053**, **CER 0.0909**, `2546/2546` file thành công.
- **Không dùng làm model chính lúc này:** `deepgram:nova-3`, `gemini:gemini-2.5-flash`, `iflytek:iat-niche`.
  - Deepgram/Gemini có nhiều output rỗng hơn trên Studio 300.

## Dataset Đã Đánh Giá

| Folder                        | Audio | Ground truth | Vai trò                             |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| `audio_samples/matched_audio` | 2277  | 32           | Dữ liệu internet/YouTube ban đầu    |
| `audio_samples/studio`        | 2548  | 2546         | Dữ liệu sạch chính để so sánh model |

Ghi chú scoring: các annotation dạng `<...>` trong ground-truth đã được bỏ qua trước khi tính WER/CER.

## Studio Full Benchmark

Đây là bảng quan trọng nhất vì dùng gần như toàn bộ ground-truth studio.

| Rank | Provider | Model | Coverage | WER | CER | Ghi chú |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | OpenAI | `gpt-4o-mini-transcribe` | 2546/2546 | **0.1764** | **0.0684** | Best overall |
| 2 | Groq | `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 | Best backup/cost-sensitive |
| 3 | Deepgram | `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER gần Groq, CER kém hơn |
| 4 | Gemini | `gemini-2.5-flash` | 1619/2546 | 0.2096 | 0.1094 | Partial run, chưa full |

## matched_audio Benchmark

Tập này nhỏ hơn và nhiều tính “internet/noisy” hơn, dùng để sanity-check trên dữ liệu YouTube ban đầu.

| Rank | Provider | Model | Rows | WER | CER | Empty |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | OpenAI | `gpt-4o-mini-transcribe` | 29 | **0.2044** | 0.1295 | 0 |
| 2 | Groq | `whisper-large-v3-turbo` | 29 | 0.2234 | **0.1158** | 0 |
| 3 | Deepgram | `nova-3` | 29 | 0.2982 | 0.2010 | 2 |
| 4 | Local | `vinai/PhoWhisper-small` | 11 | 0.4317 | 0.2207 | 0 |

Common subset 11 file:

- OpenAI: WER `0.2878`, CER `0.1842`
- Groq: WER `0.3077`, CER `0.1841`
- PhoWhisper-small: WER `0.4317`, CER `0.2207`
- Deepgram: WER `0.4700`, CER `0.3531`


## Quyết Định Đề Xuất

- Dùng **OpenAI `gpt-4o-mini-transcribe`** để tạo transcript chính cho pipeline TTS.
- Dùng **Groq `whisper-large-v3-turbo`** làm baseline/backup rẻ hơn.
- Luôn filter trước khi đưa vào dataset TTS:
  - empty hypothesis
  - WER/CER cao bất thường
  - nhiều silence/noise/music
  - transcript có annotation hoặc text không phải lời thoại
- Chưa nên quyết production chỉ bằng WER/CER; nên thêm manual spot-check, latency, cost/hour, và domain-specific intent/slot accuracy.


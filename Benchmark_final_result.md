# Benchmark Final Result

## Verdict

- **Chọn chính:** `openai:gpt-4o-mini-transcribe`
  - Studio full: **WER 0.1764**, **CER 0.0684**
  - Chạy đủ `2546/2546` file studio
  - Không có empty output trong Studio 300
- **Backup tốt nhất:** `groq:whisper-large-v3-turbo`
  - Studio full: **WER 0.2053**, **CER 0.0909**
  - Chạy đủ `2546/2546` file studio
  - Không có empty output trong Studio 300
- **Chưa chọn làm model chính:** Deepgram, Gemini, iFLYTEK
  - Deepgram/Gemini có nhiều empty output hơn
  - iFLYTEK chưa benchmark được vì lỗi auth `401 apikey not found`

Ghi chú: khi tính WER/CER, ground-truth đã bỏ qua annotation dạng `<...>`.

## Dataset

| Dataset | Audio | Ground truth | Mục đích |
| --- | ---: | ---: | --- |
| `matched_audio` | 2277 | 32 | Dữ liệu internet/YouTube ban đầu |
| `studio` | 2548 | 2546 | Dữ liệu sạch chính để chọn model |

## 1. Studio Full

Bảng quan trọng nhất vì dùng gần như toàn bộ ground-truth studio.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | OpenAI `gpt-4o-mini-transcribe` | 2546/2546 | **0.1764** | **0.0684** | Best overall |
| 2 | Groq `whisper-large-v3-turbo` | 2546/2546 | 0.2053 | 0.0909 | Best backup |
| 3 | Deepgram `nova-3` | 2546/2546 | 0.2063 | 0.1104 | WER ổn, CER kém hơn |
| 4 | Gemini `gemini-2.5-flash` | 1619/2546 | 0.2096 | 0.1094 | Chưa chạy full |

## 2. Studio 300

Bảng này dùng để nhìn nhanh empty output và so sánh cùng một tập 300 file.

| Rank | Model | Empty | WER | CER |
| ---: | --- | ---: | ---: | ---: |
| 1 | OpenAI `gpt-4o-mini-transcribe` | **0** | **0.1814** | **0.0668** |
| 2 | Groq `whisper-large-v3-turbo` | **0** | 0.2135 | 0.0851 |
| 3 | Deepgram `nova-3` | 21 | 0.2259 | 0.1286 |
| 4 | Gemini `gemini-2.5-flash` | 8 | 0.2346 | 0.1256 |

Quality nhanh của Studio 300:

- PASS: `16/300`
- REVIEW: `284/300`
- Duration TB: `8.85s`
- SNR TB: `50.00 dB`
- Silence ratio TB: `0.408`

## 3. matched_audio

Tập này nhỏ hơn, dùng để kiểm tra thêm trên dữ liệu internet/YouTube.

| Rank | Model | Rows | WER | CER | Empty |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | OpenAI `gpt-4o-mini-transcribe` | 29 | **0.2044** | 0.1295 | 0 |
| 2 | Groq `whisper-large-v3-turbo` | 29 | 0.2234 | **0.1158** | 0 |
| 3 | Deepgram `nova-3` | 29 | 0.2982 | 0.2010 | 2 |
| 4 | Local `vinai/PhoWhisper-small` | 11 | 0.4317 | 0.2207 | 0 |

## iFLYTEK

- Model: `iflytek:iat-niche`
- Đã thử: `1200` file studio đầu
- Thành công: `0`
- Lỗi: `401 Unauthorized`, `apikey not found`
- Kết luận: chưa thể so sánh WER/CER cho iFLYTEK cho tới khi key/endpoint đúng service.

## Final Recommendation

- Dùng **OpenAI `gpt-4o-mini-transcribe`** để tạo transcript chính.
- Dùng **Groq `whisper-large-v3-turbo`** làm model backup hoặc lựa chọn tiết kiệm hơn.
- Luôn filter trước khi đưa transcript vào dataset TTS:
  - empty output
  - WER/CER cao bất thường
  - audio nhiều silence/noise/music
  - transcript có annotation hoặc text không phải lời thoại

## Artifacts

- `outputs/studio_full_benchmark_checkpoint_state.md`
- `outputs/studio_300_benchmark_summary.md`
- `outputs/initial_audio_samples_evaluation.md`
- `outputs/studio_1200_iflytek_evaluation_result.md`

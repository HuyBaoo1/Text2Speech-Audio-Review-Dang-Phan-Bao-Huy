# OpenAI Parallel Benchmark

Generated: 2026-06-23T07:24:53+00:00

### OpenAI Parallel Benchmark (Generated)

Các model được chạy đồng thời; mỗi model checkpoint sau từng audio và có thể resume bằng cùng lệnh.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | Gemini `gemini-3-flash-preview` | 42/2546 | 0.1833 | 0.0847 | Partial, có thể resume |

Kết luận ngắn:
- **Tốt nhất trong lượt chạy này:** Gemini `gemini-3-flash-preview` (WER 0.1833, CER 0.0847).
- Các model chưa đủ coverage sẽ tự tiếp tục từ checkpoint; các dòng đã hoàn tất không bị gọi lại.

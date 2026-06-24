# OpenAI Parallel Benchmark

Generated: 2026-06-24T06:53:27+00:00

### OpenAI Parallel Benchmark (Generated)

Các model được chạy đồng thời; mỗi model checkpoint sau từng audio và có thể resume bằng cùng lệnh.

| Rank | Model | Coverage | WER | CER | Kết luận |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | Gemini `gemini-3-flash-preview` | 2544/2546 | 0.1710 | 0.0701 | 2 lỗi API; lần sau sẽ retry các dòng lỗi |

Kết luận ngắn:
- **Tốt nhất trong lượt chạy này:** Gemini `gemini-3-flash-preview` (WER 0.1710, CER 0.0701).
- Các model chưa đủ coverage sẽ tự tiếp tục từ checkpoint; các dòng đã hoàn tất không bị gọi lại.

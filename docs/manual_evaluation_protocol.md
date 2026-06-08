# Manual Evaluation Protocol

Tập đầu tiên chỉ lấy 100 audio đầu từ `audio_samples/matched_audio`. Mục tiêu không phải đạt benchmark đẹp ngay, mà là hiểu lỗi pipeline/model trên data thật.

## Quy Trình

1. Chạy `create_manifest.py`.
2. Chạy `run_quality_analysis.py`.
3. Nghe nhanh các clip fail quality gate để xem fail thật hay chỉ fail heuristic.
4. Chọn 20-30 clip đại diện để viết ground truth vào `data/ground_truth`.
5. Chạy ít nhất một model local và một API model nếu có quota.
6. So sánh WER/CER và manual accept.
7. Ghi lỗi vào `manual_error_tags`.

## Rubric Cho Clip

`usable_for_tts=yes`

- single speaker
- transcript có thể viết chính xác
- không nhạc nền/noise nặng
- không clipping nghe rõ
- duration hợp lý

`usable_for_tts=maybe`

- cần trim silence
- cần normalize loudness
- ASR sai nhưng người nghe vẫn transcribe được
- có noise nhẹ

`usable_for_tts=no`

- multi-speaker overlap
- nhạc nền mạnh
- speech bị méo/clipping
- transcript không chắc
- clip quá ngắn/dài
- non-speech

## Rubric Cho ASR

Đánh giá ASR bằng cả metric và review:

- `wer`, `cer`: tốt để so sánh định lượng nếu có ground truth.
- `manual_accept=yes/no`: transcript có đủ tốt để bootstrap labeling không.
- `manual_error_tags`: `hallucination`, `missed_words`, `number_error`, `name_error`, `punctuation`, `code_switch`, `bad_language_detect`.

WER thấp chưa đủ cho TTS. Một transcript có dấu câu, số, tên riêng hoặc code-switch sai vẫn có thể làm hỏng dataset training.

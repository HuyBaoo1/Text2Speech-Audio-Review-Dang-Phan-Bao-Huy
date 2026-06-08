# TTS Data Quality

Data TTS chất lượng cao không chỉ là audio nghe rõ. Nó là cặp audio-text đủ sạch, đủ chính xác, đủ nhất quán để model học pronunciation, rhythm, speaker identity và prosody thay vì học noise.

## Audio Tốt Cần Gì

- Một speaker chính trong mỗi segment.
- Ít background music, reverb, compression artifact, tiếng xe/quạt/room noise.
- Không clipping. Clipping dễ tạo giọng TTS bị gắt hoặc méo.
- Loudness ổn định giữa các clip cùng speaker.
- Không cắt mất đầu/cuối từ.
- Segment thường nên khoảng 2-15 giây; dưới 1 giây thường thiếu context, trên 20 giây khó batch/training và dễ lỗi transcript.
- Sample rate/channels thống nhất sau preprocessing.

## Transcript Tốt Cần Gì

- Khớp chính xác lời nói.
- Không thêm từ ASR hallucination.
- Không bỏ sót từ nhỏ nhưng ảnh hưởng prosody.
- Chuẩn hóa số, ngày tháng, ký hiệu, viết tắt theo cùng một rule.
- Với code-switching, cần giữ language metadata hoặc tag riêng.
- Không lẫn speaker turn trong một transcript nếu model không hỗ trợ multi-speaker.

## Metadata Tối Thiểu

- `speaker_id`
- `language`
- `source_url`
- license/risk note
- start/end time nếu cắt từ video dài
- preprocessing history
- manual review status

## Quality Gate Ban Đầu Trong Project

Project đang gate bằng:

- duration: 1-20s
- SNR >= 20dB
- silence ratio <= 0.35
- clipping ratio <= 0.001
- absolute DC offset <= 0.02

Đây là gate để ưu tiên review, không phải luật tuyệt đối. Clip fail gate vẫn có thể dùng nếu manual review thấy tốt sau trim hoặc normalize.

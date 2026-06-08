# Pipeline Design For YouTube-to-TTS Dataset

Pipeline nên được chia thành các module độc lập để thay model dễ và đo được chất lượng từng bước.

## Module Đề Xuất

1. Source ingestion
   - input: YouTube URL/local audio
   - output: source media + metadata
   - model/tool: yt-dlp hoặc downloader tương đương

2. Audio standardization
   - convert format, sample rate, mono/stereo, loudness
   - output: audio chuẩn để xử lý tiếp

3. Speech activity detection
   - tìm đoạn có speech, bỏ silence dài
   - model/tool: WebRTC VAD, Silero VAD, pyannote segmentation

4. Speaker diarization
   - phát hiện multi-speaker
   - model/tool: pyannote speaker diarization, SpeechBrain

5. Music/noise detection
   - loại speech có nhạc nền hoặc noise quá mạnh
   - model/tool: YAMNet/PANNs/audio tagging, heuristic SNR

6. Segmentation
   - cắt utterance 2-15s, không cắt giữa từ/câu
   - kết hợp VAD + ASR timestamp

7. ASR transcription
   - sinh transcript candidate từ nhiều backend
   - model/tool: Whisper local, faster-whisper, paid API

8. Text normalization
   - chuẩn hóa punctuation, số, ký hiệu, abbreviations
   - rule cần khớp recipe training TTS

9. Quality scoring
   - combine audio metrics, diarization, ASR confidence, manual label
   - output: accept/maybe/reject

10. Dataset export
   - output: wav/text/metadata theo format trainer cần

## Tại Sao ASR Là Module Trung Tâm

Với TTS, transcript sai là lỗi rất độc. Audio sạch nhưng text lệch sẽ dạy model mapping sai giữa âm thanh và chữ. Vì vậy ASR không nên được xem là "tool transcribe một lần", mà là model comparison layer:

- chạy nhiều backend trên cùng sample
- lưu transcript + model + provider + runtime/cost
- so với ground truth bằng WER/CER
- manual tag lỗi: hallucination, missed words, number error, name error, punctuation error, code-switching
- chọn backend theo loại audio/language/domain

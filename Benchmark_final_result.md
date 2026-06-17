# Benchmark Final Result

## Executive Summary

- Best model hiện tại: `openai:gpt-4o-mini-transcribe`.
- Lý do chọn: WER/CER thấp nhất trên cả `matched_audio` và `studio`, không có hypothesis rỗng trong các tập đã chấm.
- Model thay thế nếu ưu tiên quota/free/chi phí: `groq:whisper-large-v3-turbo`.
- Không khuyến nghị dùng `deepgram:nova-3` hoặc `gemini:gemini-2.5-flash` làm transcript tự động chính cho TTS ở thời điểm này vì có nhiều hypothesis rỗng hơn trên Studio 300.
- Khi scoring, ground-truth đã bỏ qua annotation dạng `<...>` trước khi tính WER/CER.

## Dataset Coverage

- `audio_samples/matched_audio`
  - Audio: `2277` WAV.
  - Ground-truth: `32` TXT trong `data/ground_truth`.
  - Benchmark chính: subset nhỏ có ground-truth, dùng để kiểm tra dữ liệu YouTube/internet ban đầu.
- `audio_samples/studio`
  - Audio: `2548` WAV.
  - Ground-truth: `2546` TXT trong `data/ground_truth_studio`.
  - Benchmark chính: Studio cho so sánh nhanh; full checkpoint đã có cho OpenAI/Groq/Deepgram.

## Result: matched_audio

- Quality subset: `100` audio đầu.
- Quality gate: PASS `50/100`, REVIEW `50/100`.
- Duration TB: `16.08s`; SNR TB: `46.13 dB`; silence ratio TB: `0.296`.
- Ranking theo own scored subset:
  - #1 OpenAI `gpt-4o-mini-transcribe`: `29` rows, WER `0.2044`, CER `0.1295`, empty `0`.
  - #2 Groq `whisper-large-v3-turbo`: `29` rows, WER `0.2234`, CER `0.1158`, empty `0`.
  - #3 Deepgram `nova-3`: `29` rows, WER `0.2982`, CER `0.2010`, empty `2`.
  - #4 Local `vinai/PhoWhisper-small`: `11` rows, WER `0.4317`, CER `0.2207`, empty `0`.
- Fair common subset `11` files:
  - OpenAI vẫn đứng đầu: WER `0.2878`, CER `0.1842`.
  - Groq rất sát: WER `0.3077`, CER `0.1841`.

## Result: studio

- Studio 300 quality:
  - Target: `300` audio đầu có ground-truth.
  - Quality gate: PASS `16/300`, REVIEW `284/300`.
  - Duration TB: `8.85s`; SNR TB: `50.00 dB`; silence ratio TB: `0.408`.
- Studio 300 ASR ranking:
  - #1 OpenAI `gpt-4o-mini-transcribe`: `300/300`, WER `0.181432`, CER `0.066774`, empty `0`.
  - #2 Groq `whisper-large-v3-turbo`: `300/300`, WER `0.213490`, CER `0.085053`, empty `0`.
  - #3 Deepgram `nova-3`: `300/300`, WER `0.225865`, CER `0.128594`, empty `21`.
  - #4 Gemini `gemini-2.5-flash`: `300/300`, WER `0.234580`, CER `0.125562`, empty `8`.
- Studio full checkpoint:
  - OpenAI: complete `2546/2546`, WER `0.176369`, CER `0.068363`.
  - Groq: complete `2546/2546`, WER `0.205306`, CER `0.090900`.
  - Deepgram: complete `2546/2546`, WER `0.206261`, CER `0.110441`.
  - Gemini: partial `1619/2546`, WER `0.209589`, CER `0.109404`.

## Recommendation

- Primary ASR for building TTS transcript pipeline: `openai:gpt-4o-mini-transcribe`.
- Secondary/cost-sensitive ASR: `groq:whisper-large-v3-turbo`.
- Use Deepgram/Gemini as comparison models only until empty-output cases are inspected.
- For production dataset creation, do not accept ASR transcript by WER alone:
  - Add manual spot-check on low-confidence/high-WER rows.
  - Filter empty/very short hypotheses.
  - Track speaker consistency, noise/music overlap, silence ratio, clipping, and transcript normalization.
  - Keep `--resume --checkpoint-every 10` for all provider runs to avoid rerunning completed audio.

## Key Artifacts

- `outputs/initial_audio_samples_evaluation.md`
- `outputs/studio_300_benchmark_summary.md`
- `outputs/studio_full_benchmark_checkpoint_state.md`
- `outputs/studio_full_asr_eval_openai_gpt_4o_mini.csv`
- `outputs/studio_full_asr_eval_groq_whisper_large_v3_turbo.csv`
- `outputs/studio_full_asr_eval_deepgram_nova3.csv`
- `outputs/studio_full_asr_eval_gemini_2_5_flash.csv`

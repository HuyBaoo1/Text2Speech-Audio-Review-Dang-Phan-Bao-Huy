# Studio 300 Benchmark Summary

Ground-truth annotations inside `<...>` are stripped before scoring.

- Target rows: 300 first studio audio files with ground truth.
- Quality PASS: 16/300; REVIEW: 284/300.
- Mean duration: 8.85s; mean SNR: 50.00 dB; mean silence ratio: 0.408.

| Rank | Provider | Model | Scored | Missing | Empty | WER mean | CER mean |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | openai | `gpt-4o-mini-transcribe` | 300/300 | 0 | 0 | 0.181432 | 0.066774 |
| 2 | groq | `whisper-large-v3-turbo` | 300/300 | 0 | 0 | 0.213490 | 0.085053 |
| 3 | deepgram | `nova-3` | 300/300 | 0 | 21 | 0.225865 | 0.128594 |
| 4 | gemini | `gemini-2.5-flash` | 300/300 | 0 | 8 | 0.234580 | 0.125562 |

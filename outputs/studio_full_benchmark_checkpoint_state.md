# Studio Full Benchmark Checkpoint

Generated: 2026-06-17T15:46:48

| Provider | Model | Status | Success | Remaining | Errors | WER mean | CER mean |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-4o-mini-transcribe` | complete | 2546/2546 | 0 | 0 | 0.176369 | 0.068363 |
| groq | `whisper-large-v3-turbo` | complete | 2546/2546 | 0 | 0 | 0.205306 | 0.090900 |
| deepgram | `nova-3` | complete | 2546/2546 | 0 | 0 | 0.206261 | 0.110441 |
| gemini | `gemini-2.5-flash` | partial | 1619/2546 | 927 | 0 | 0.209589 | 0.109404 |

For new paid/free-quota model tests, prefer `--limit 300 --resume --checkpoint-every 10`.

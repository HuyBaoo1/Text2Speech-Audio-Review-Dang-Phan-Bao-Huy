# Evaluation Result

Run date: 2026-06-10

## Scope

- Dataset folder: `audio_samples/matched_audio`
- Sample window: first 100 audio files
- Ground truth files found: 30
- Non-empty ground truth used for scoring: 29
- Empty ground truth excluded: `data/ground_truth/-aCDck13cRI_69.txt`

## Audio Quality Result

| metric | value |
| --- | ---: |
| clips analyzed | 100 |
| quality gate pass | 50 |
| quality gate review | 50 |
| average duration | 16.08s |
| min duration | 3.24s |
| max duration | 30.00s |
| average SNR | 46.13 dB |

## ASR Benchmark Result

| rank | provider | model | status | GT matched | WER avg | CER avg | best WER | worst WER |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | OpenAI | `gpt-4o-mini-transcribe` | rescored existing output | 29 | 0.2044 | 0.1295 | 0.0238 | 0.6400 |
| 2 | Groq | `whisper-large-v3-turbo` | rerun ok | 29 | 0.2234 | 0.1158 | 0.0714 | 0.5600 |
| 3 | Deepgram | `nova-3` | rerun ok | 29 | 0.2982 | 0.2010 | 0.0938 | 1.0000 |
| 4 | local-whisper | `vinai/PhoWhisper-small` | previous 11-file result only | 11 | 0.4317 | 0.2207 | 0.2254 | 0.9200 |
| - | Gemini | `gemini-2.5-flash` | failed HTTP 503 high demand | 0 |  |  |  |  |
| - | ElevenLabs | `scribe_v2` | missing key | 0 |  |  |  |  |
| - | Azure Speech | `azure-short-audio` | missing key | 0 |  |  |  |  |

## Takeaways

- OpenAI currently has the best average WER.
- Groq has the best average CER and best worst-case WER among completed 29-file runs, so it is a strong free-quota candidate.
- Deepgram is working but underperforms OpenAI/Groq on the current Vietnamese set.
- `-Yg0ClzBn2k_62.wav` is consistently difficult and should be manually inspected.
- Gemini is integrated but temporarily unavailable/high demand for the current key/session.

## Updated Artifacts

- `data/manual_eval_manifest.csv`
- `outputs/asr_eval_openai_scored.csv`
- `outputs/asr_eval_groq_whisper_large_v3_turbo_scored.csv`
- `outputs/asr_eval_deepgram_nova3_scored.csv`
- `outputs/benchmark_free_vi_summary.csv`
- `outputs/benchmark_vi_models.md`
- `outputs/evaluation_summary.md`

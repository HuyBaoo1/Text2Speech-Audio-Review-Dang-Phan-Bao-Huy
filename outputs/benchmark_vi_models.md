# Vietnamese ASR Benchmark

Benchmark subset: 18 audio files with non-empty ground truth in `data/ground_truth`.

One ground-truth file is currently empty and excluded from scoring:

- `data/ground_truth/-aCDck13cRI_69.txt`

## Results

| model | provider | status | GT matched | WER avg | CER avg | best WER | worst WER |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini-transcribe` | OpenAI | existing API result, rescored | 18 | 0.2238 | 0.1390 | 0.0625 | 0.6400 |
| `whisper-large-v3-turbo` | Groq | ok | 18 | 0.2565 | 0.1427 | 0.0938 | 0.5600 |
| `nova-3` | Deepgram | ok | 18 | 0.3620 | 0.2537 | 0.0938 | 1.0000 |
| `vinai/PhoWhisper-small` | local-whisper | previous 11-file run only; 18-file CPU run failed | 11 | 0.4317 | 0.2207 | 0.2254 | 0.9200 |
| `gemini-2.5-flash` | Gemini | failed: free quota/rate limit HTTP 429 | 0 |  |  |  |  |
| `scribe_v2` | ElevenLabs | missing `ELEVENLABS_API_KEY` | 0 |  |  |  |  |
| `azure-short-audio` | Azure Speech | missing `AZURE_SPEECH_KEY` | 0 |  |  |  |  |

## Current Ranking

1. `gpt-4o-mini-transcribe`: best average WER/CER on the 18-file ground-truth subset.
2. `whisper-large-v3-turbo`: close to OpenAI on CER and best worst-case WER among the completed 18-file runs.
3. `nova-3`: usable, but worse average WER/CER on this subset.
4. `vinai/PhoWhisper-small`: free local Vietnamese baseline; needs a more stable local run before comparing on the full 18-file subset.

## Best/Worst Files

Groq:

- Best WER: `-Yg0ClzBn2k_143.wav` at 0.0938
- Worst WER: `-Yg0ClzBn2k_62.wav` at 0.5600

Deepgram:

- Best WER: `-Yg0ClzBn2k_143.wav` at 0.0938
- Worst WER: `-Yg0ClzBn2k_62.wav` at 1.0000

## Notes

- `outputs/asr_eval_openai.csv` was not called again; it was rescored offline with the newly added ground truth.
- Groq and Deepgram were called with configured free-quota keys.
- Gemini started but hit HTTP 429 quota/rate limit, so no scored Gemini report was produced.
- ElevenLabs and Azure were skipped because their keys are not configured in `.env`.
- `PhoWhisper-small` was previously scored on 11 files. Expanding it to 18 files on CPU failed after model load, likely due local resource constraints.

## Artifacts

- `outputs/asr_eval_openai_scored.csv`
- `outputs/asr_eval_groq_whisper_large_v3_turbo_scored.csv`
- `outputs/asr_eval_deepgram_nova3_scored.csv`
- `outputs/asr_eval_phowhisper_small_scored.csv`
- `outputs/benchmark_free_vi_summary.csv`

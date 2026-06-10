# Vietnamese ASR Benchmark

Benchmark subset: 29 audio files with non-empty ground truth in `data/ground_truth`.

One ground-truth file is currently empty and excluded from scoring:

- `data/ground_truth/-aCDck13cRI_69.txt`

## Results

| model | provider | status | GT matched | WER avg | CER avg | best WER | worst WER |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini-transcribe` | OpenAI | existing API result, rescored offline | 29 | 0.2044 | 0.1295 | 0.0238 | 0.6400 |
| `whisper-large-v3-turbo` | Groq | ok | 29 | 0.2234 | 0.1158 | 0.0714 | 0.5600 |
| `nova-3` | Deepgram | ok | 29 | 0.2982 | 0.2010 | 0.0938 | 1.0000 |
| `vinai/PhoWhisper-small` | local-whisper | previous 11-file run only; skipped in latest run | 11 | 0.4317 | 0.2207 | 0.2254 | 0.9200 |
| `gemini-2.5-flash` | Gemini | failed: HTTP 503 high demand | 0 |  |  |  |  |
## Current Ranking

1. `gpt-4o-mini-transcribe`: best average WER on the current subset.
2. `whisper-large-v3-turbo`: best average CER and strongest worst-case WER among completed 29-file runs.
3. `nova-3`: usable, but weaker than OpenAI/Groq for this Vietnamese sample set.
4. `vinai/PhoWhisper-small`: free local baseline; needs a stable full-subset run.

## Notes

- `outputs/asr_eval_openai.csv` was not called again; it was rescored offline with the newly added ground truth.
- Groq and Deepgram were called again with configured free-quota keys.
- Gemini started but returned HTTP 503 high demand, so no scored Gemini report was produced.

## Artifacts

- `outputs/asr_eval_openai_scored.csv`
- `outputs/asr_eval_groq_whisper_large_v3_turbo_scored.csv`
- `outputs/asr_eval_deepgram_nova3_scored.csv`
- `outputs/asr_eval_phowhisper_small_scored.csv`
- `outputs/benchmark_free_vi_summary.csv`

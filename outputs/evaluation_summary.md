# Evaluation Summary

## Dataset

- Source folder: `audio_samples/matched_audio`
- Evaluated sample count: `100`
- Ground truth files: `30`
- Non-empty ground truth used for ASR scoring: `29`
- Excluded empty ground truth file: `data/ground_truth/-aCDck13cRI_69.txt`

## Audio Quality

- Quality gate pass: `50`
- Quality gate review: `50`
- Average duration: `16.08s`
- Min duration: `3.24s`
- Max duration: `30.00s`
- Average SNR: `46.13 dB`

## ASR Benchmark

| model | provider | status | GT matched | WER avg | CER avg | best WER | worst WER |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-4o-mini-transcribe` | OpenAI | existing API result, rescored offline | 29 | 0.2044 | 0.1295 | 0.0238 | 0.6400 |
| `whisper-large-v3-turbo` | Groq | ok | 29 | 0.2234 | 0.1158 | 0.0714 | 0.5600 |
| `nova-3` | Deepgram | ok | 29 | 0.2982 | 0.2010 | 0.0938 | 1.0000 |
| `vinai/PhoWhisper-small` | local-whisper | previous 11-file run only; skipped in latest run | 11 | 0.4317 | 0.2207 | 0.2254 | 0.9200 |
| `gemini-2.5-flash` | Gemini | failed: HTTP 503 high demand | 0 |  |  |  |  |

## Current Ranking

1. `gpt-4o-mini-transcribe`: best average WER on the 29-file ground-truth subset.
2. `whisper-large-v3-turbo`: best average CER and best worst-case WER among completed 29-file runs.
3. `nova-3`: usable, but clearly weaker on this subset.
4. `vinai/PhoWhisper-small`: useful free local baseline, but not comparable on the full 29-file subset yet.

## Best/Worst Files

OpenAI:

- Best WER: `04jhP_1G24M_10.wav` at 0.0238
- Worst WER: `-Yg0ClzBn2k_62.wav` at 0.6400

Groq:

- Best WER: `04jhP_1G24M_10.wav` at 0.0714
- Worst WER: `-Yg0ClzBn2k_62.wav` at 0.5600

Deepgram:

- Best WER: `-Yg0ClzBn2k_143.wav` at 0.0938
- Worst WER: `-Yg0ClzBn2k_62.wav` at 1.0000

## Interpretation

- OpenAI currently has the best WER, while Groq has the best CER and slightly better worst-case WER.
- Groq is close enough to OpenAI to be worth expanding if free quota remains.
- Deepgram should be kept as a comparison provider, but its current Vietnamese results are weaker on this dataset.
- `-Yg0ClzBn2k_62.wav` is the hardest current sample across providers and should be manually reviewed for noise, language mix, or transcript ambiguity.
- Gemini is integrated but did not complete because the service returned HTTP 503 high demand.
- ElevenLabs and Azure are integrated but still need free-quota keys in `.env`.

## Artifacts

- `outputs/quality_report.csv`
- `outputs/asr_eval_openai_scored.csv`
- `outputs/asr_eval_groq_whisper_large_v3_turbo_scored.csv`
- `outputs/asr_eval_deepgram_nova3_scored.csv`
- `outputs/asr_eval_phowhisper_small_scored.csv`
- `outputs/benchmark_free_vi_summary.csv`
- `outputs/benchmark_vi_models.md`
- `outputs/evaluation_result.md`

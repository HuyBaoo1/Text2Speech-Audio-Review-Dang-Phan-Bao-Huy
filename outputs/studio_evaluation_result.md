# Studio Evaluation Result

Run date: 2026-06-15

## Scope

- Audio folder: `audio_samples/studio`
- Studio audio files: `2548`
- Imported ground truth rows: `2546`
- Imported ground truth files: `2546`
- Studio audio without ground truth:
  - `19052026_omni_Vi-ai_59_chunk003.wav`
  - `19052026_omni_Vi-ai_83_chunk018.wav`
- Benchmark subset: first `100` studio audio files with ground truth

## Ground Truth Import

Ground truth was imported from:

- `data/imported_ground_truth/omni_vi_ai_ground_truth.csv`

Generated transcript files:

- `data/ground_truth_studio/*.txt`

Import result:

| metric | value |
| --- | ---: |
| imported transcript files | 2546 |
| missing audio rows | 0 |
| empty transcript rows | 0 |

## Audio Quality Result

Quality report:

- `outputs/studio_quality_report.csv`

| metric | value |
| --- | ---: |
| clips analyzed | 100 |
| quality gate pass | 4 |
| quality gate review | 96 |
| average duration | 8.34s |
| min duration | 1.79s |
| max duration | 22.78s |
| average SNR | 49.37 dB |
| average silence ratio | 0.415 |

Interpretation:

- Studio audio has strong SNR, so it is cleaner than the previous YouTube-derived batch by noise metrics.
- The current quality gate is too strict for this studio set because `max_silence=0.35` marks most files as review.
- For studio-style assistant speech, silence/pauses may be normal. Consider a studio-specific gate such as `max_silence=0.50`.

## ASR Benchmark Result

All rows below were evaluated on the same 100 studio clips with ground truth.

| rank | provider | model | GT matched | WER avg | CER avg | best WER | worst WER | empty hypotheses |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | OpenAI | `gpt-4o-mini-transcribe` | 100 | 0.1862 | 0.0628 | 0.0556 | 0.8333 | 0 |
| 2 | Groq | `whisper-large-v3-turbo` | 100 | 0.2093 | 0.0828 | 0.0000 | 0.8333 | 0 |
| 3 | Gemini | `gemini-2.5-flash` | 100 | 0.2305 | 0.1206 | 0.0455 | 1.1351 | 3 |
| 4 | Deepgram | `nova-3` | 100 | 0.2343 | 0.1337 | 0.0408 | 1.0000 | 7 |

## Best/Worst Cases

OpenAI:

- Best WER: `16052026_omni_Vi-ai_02_chunk004.wav` at 0.0556
- Worst WER: `16052026_omni_Vi-ai_03_chunk010.wav` at 0.8333

Groq:

- Best WER: `16052026_omni_Vi-ai_01_chunk014.wav` at 0.0000
- Worst WER: `16052026_omni_Vi-ai_03_chunk010.wav` at 0.8333

Gemini:

- Best WER: `16052026_omni_Vi-ai_04_chunk010.wav` at 0.0455
- Worst WER: `16052026_omni_Vi-ai_04_chunk003.wav` at 1.1351

Deepgram:

- Best WER: `16052026_omni_Vi-ai_02_chunk020.wav` at 0.0408
- Worst WER: `16052026_omni_Vi-ai_03_chunk022.wav` at 1.0000

## Takeaways

- OpenAI `gpt-4o-mini-transcribe` is currently the best overall model on this 100-file studio subset.
- Groq `whisper-large-v3-turbo` is close to OpenAI and has the lowest best-case WER, making it a strong free-quota candidate.
- Gemini completed successfully this time, but it produced 3 empty hypotheses and a higher average WER/CER than OpenAI/Groq.
- Deepgram worked, but it produced 7 empty hypotheses and the weakest aggregate score among the four completed providers.
- The studio data is clean by SNR but pause-heavy, so audio quality filtering should be tuned separately from the YouTube-derived batch.
- WER can exceed 1.0 when an ASR output inserts substantially more words than the reference.

## Artifacts

- `data/ground_truth_studio/`
- `data/studio_manual_eval_manifest.csv`
- `outputs/studio_quality_report.csv`
- `outputs/studio_asr_eval_openai_gpt_4o_mini_scored.csv`
- `outputs/studio_asr_eval_groq_whisper_large_v3_turbo_scored.csv`
- `outputs/studio_asr_eval_gemini_2_5_flash_scored.csv`
- `outputs/studio_asr_eval_deepgram_nova3_scored.csv`
- `outputs/studio_benchmark_all_models_summary.csv`
- `outputs/studio_benchmark_free_vi_summary.csv`

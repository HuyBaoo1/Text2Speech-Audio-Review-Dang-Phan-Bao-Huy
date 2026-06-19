# Gemini 2.5 Flash Studio Checkpoint

Date: 2026-06-18

## Provider

- Provider: `gemini`
- Model: `gemini-2.5-flash`
- Dataset: `audio_samples/studio`
- Ground truth: `data/ground_truth_studio`
- Language: `Vietnamese`

## Studio Full State

| Metric | Value |
| --- | ---: |
| Total selected rows | 2546 |
| Scored rows | 2546 |
| Error rows | 0 |
| Empty hypotheses | 53 |
| WER mean | 0.216120 |
| CER mean | 0.111884 |

## Studio 300 State

| Metric | Value |
| --- | ---: |
| Selected rows | 300 |
| Scored rows | 300 |
| Empty hypotheses | 8 |
| WER mean | 0.234747 |
| CER mean | 0.127327 |

## matched_audio State

| Metric | Value |
| --- | ---: |
| Rows | 31 |
| Scored rows | 31 |
| Error rows | 0 |
| WER mean | 0.205650 |
| CER mean | 0.114894 |

## Checkpoint Files

- Studio CSV: `outputs/studio_full_asr_eval_gemini_2_5_flash.csv`
- Studio JSONL: `outputs/studio_full_asr_eval_gemini_2_5_flash.jsonl`
- matched_audio CSV: `outputs/matched_asr_eval_gemini_2_5_flash.csv`
- matched_audio JSONL: `outputs/matched_asr_eval_gemini_2_5_flash.jsonl`

The benchmark runner can resume with `--resume`; no rows currently need retry.

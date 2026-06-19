# ElevenLabs Studio Checkpoint

Date: 2026-06-18

## Provider

- Provider: `elevenlabs`
- Model: `scribe_v2`
- Dataset: `audio_samples/studio`
- Ground truth: `data/ground_truth_studio`
- Language: `vie`

## Current State

| Metric | Value |
| --- | ---: |
| Total selected rows | 2546 |
| Scored rows | 2544 |
| Error rows currently in CSV | 0 |
| Ground-truth annotation-only rows skipped | 2 |
| Empty scored hypotheses | 0 |
| WER mean on scored rows | 0.123340 |
| CER mean on scored rows | 0.045047 |

## Checkpoint Files

- CSV: `outputs/studio_full_asr_eval_elevenlabs_scribe_v2.csv`
- JSONL: `outputs/studio_full_asr_eval_elevenlabs_scribe_v2.jsonl`

The benchmark runner uses `--resume` and skips rows that already have successful transcripts.
The current run is complete for all scoreable studio rows.

## Resume Command

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider elevenlabs --model scribe_v2 --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vie --limit 0 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_full_asr_eval_elevenlabs_scribe_v2.csv --output-jsonl outputs\studio_full_asr_eval_elevenlabs_scribe_v2.jsonl
```

## Completion Note

After enabling the Speech-to-Text permission, ElevenLabs completed the scoreable studio set. Two rows are not scored because their ground-truth becomes empty after stripping annotation tags such as `<sigh>`.

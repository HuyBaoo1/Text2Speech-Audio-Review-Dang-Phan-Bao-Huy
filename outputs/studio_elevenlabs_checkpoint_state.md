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
| Scored rows | 980 |
| Error rows currently in CSV | 1566 |
| Current-key quota errors | 193 |
| Empty scored hypotheses | 0 |
| WER mean on scored rows | 0.117916 |
| CER mean on scored rows | 0.039755 |

## Checkpoint Files

- CSV: `outputs/studio_full_asr_eval_elevenlabs_scribe_v2.csv`
- JSONL: `outputs/studio_full_asr_eval_elevenlabs_scribe_v2.jsonl`

The benchmark runner uses `--resume` and skips rows that already have successful transcripts.
Rows with `manual_notes` beginning with `ERROR:` will be retried, so the next run should continue from the unscored files without re-running the 980 successful rows.

## Resume Command

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider elevenlabs --model scribe_v2 --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vie --limit 0 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_full_asr_eval_elevenlabs_scribe_v2.csv --output-jsonl outputs\studio_full_asr_eval_elevenlabs_scribe_v2.jsonl
```

## Quota Note

ElevenLabs returned `quota_exceeded` after 980 scored files. Do not retry until the account has renewed credits or a paid/additional quota is available.

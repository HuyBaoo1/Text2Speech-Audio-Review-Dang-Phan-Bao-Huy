# Studio Full Benchmark Checkpoint

Generated: 2026-06-16T17:49:55

Dataset:
- Studio audio files: 2548
- Studio ground-truth files: 2546
- Target files for ASR scoring: 2546
- Quality report: `outputs/studio_full_quality_report.csv`

Resume rule: run the same command with `--resume --checkpoint-every 10 --limit 0 --only-ground-truth`. Successful rows are skipped; `ERROR:` rows are retried.

| Provider | Model | Status | Saved rows | Successful scored | Remaining | Errors | WER mean | CER mean |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| openai | `gpt-4o-mini-transcribe` | complete | 2546 | 2546 | 0 | 0 | 0.176369 | 0.068363 |
| groq | `whisper-large-v3-turbo` | partial | 2213 | 2203 | 343 | 10 | 0.200526 | 0.086687 |
| deepgram | `nova-3` | partial | 40 | 40 | 2506 | 0 | 0.215642 | 0.100752 |
| gemini | `gemini-2.5-flash` | not_started | 0 | 0 | 2546 | 0 |  |  |

Resume commands:

## openai / gpt-4o-mini-transcribe

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider openai --model gpt-4o-mini-transcribe --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --limit 0 --language vi --output-csv outputs\studio_full_asr_eval_openai_gpt_4o_mini.csv --output-jsonl outputs\studio_full_asr_eval_openai_gpt_4o_mini.jsonl --only-ground-truth --resume --checkpoint-every 10
```

## groq / whisper-large-v3-turbo

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider groq --model whisper-large-v3-turbo --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --limit 0 --language vi --output-csv outputs\studio_full_asr_eval_groq_whisper_large_v3_turbo.csv --output-jsonl outputs\studio_full_asr_eval_groq_whisper_large_v3_turbo.jsonl --only-ground-truth --resume --checkpoint-every 10
```

## deepgram / nova-3

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider deepgram --model nova-3 --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --limit 0 --language vi --output-csv outputs\studio_full_asr_eval_deepgram_nova3.csv --output-jsonl outputs\studio_full_asr_eval_deepgram_nova3.jsonl --only-ground-truth --resume --checkpoint-every 10
```

## gemini / gemini-2.5-flash

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider gemini --model gemini-2.5-flash --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --limit 0 --language Vietnamese --output-csv outputs\studio_full_asr_eval_gemini_2_5_flash.csv --output-jsonl outputs\studio_full_asr_eval_gemini_2_5_flash.jsonl --only-ground-truth --resume --checkpoint-every 10
```

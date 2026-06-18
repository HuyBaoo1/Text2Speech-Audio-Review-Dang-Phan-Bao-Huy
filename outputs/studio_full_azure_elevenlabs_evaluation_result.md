# Azure + ElevenLabs Studio Evaluation Result

## Azure Speech

- Dataset: `audio_samples/studio`
- Ground truth: `data/ground_truth_studio`
- Provider/model: `azure:azure-short-audio`
- Output CSV: `outputs/studio_full_asr_eval_azure_speech_vi_vn.csv`
- Output JSONL: `outputs/studio_full_asr_eval_azure_speech_vi_vn.jsonl`

| Metric | Value |
| --- | ---: |
| Attempted rows | 2546 |
| Scored rows | 1632 |
| Error rows | 912 |
| Empty scored hypotheses | 0 |
| WER mean | 0.236144 |
| CER mean | 0.101110 |

Main Azure errors:

- `400 Bad Request`: 885 rows
- `429 Too Many Requests`: 15 rows
- Network/SSL/connection errors: 12 rows

Interpretation:

- Azure produced usable transcripts for a large subset, but the full-run error rate is too high for production use without retry/backoff and better request validation.
- Current Azure result is weaker than OpenAI/Groq/Deepgram on full studio by WER.

## ElevenLabs

- Provider/model attempted: `elevenlabs:scribe_v2`
- Output CSV: `outputs/studio_full_asr_eval_elevenlabs_scribe_v2.csv`
- Output JSONL: `outputs/studio_full_asr_eval_elevenlabs_scribe_v2.jsonl`

| Metric | Value |
| --- | ---: |
| Attempted rows saved | 350 |
| Successful transcripts | 0 |
| Error rows | 350 |
| WER/CER | unavailable |

API review:

- Endpoint used: `POST https://api.elevenlabs.io/v1/speech-to-text`
- Auth header used: `xi-api-key`
- Model used: `scribe_v2`
- Previous direct probe error: `missing_permissions`, exact permission missing: `speech_to_text`
- Latest direct Speech-to-Text probe with the new key reached the correct endpoint but failed with `detected_unusual_activity`.
- Latest ElevenLabs message: Free Tier access is disabled for the account; upgrade to a paid subscription to continue.

Interpretation:

- The ElevenLabs adapter is structurally correct.
- The current blocker is account/key access, not request format.
- Do not run full ElevenLabs benchmark until the account has active Speech-to-Text access.

Resume command after fixing key permission:

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider elevenlabs --model scribe_v2 --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vie --limit 0 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_full_asr_eval_elevenlabs_scribe_v2.csv --output-jsonl outputs\studio_full_asr_eval_elevenlabs_scribe_v2.jsonl
```

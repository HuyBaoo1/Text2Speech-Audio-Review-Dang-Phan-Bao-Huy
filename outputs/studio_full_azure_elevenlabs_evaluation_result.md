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
| Current-key scored rows | 980 |
| Current-key quota errors | 193 |
| Remaining rows not re-run after quota stop | 1373 |
| Empty scored hypotheses | 0 |
| WER mean | 0.117916 |
| CER mean | 0.039755 |

API review:

- Endpoint used: `POST https://api.elevenlabs.io/v1/speech-to-text`
- Auth header used: `xi-api-key`
- Model used: `scribe_v2`
- Previous direct probe error: `missing_permissions`, exact permission missing: `speech_to_text`
- Previous Speech-to-Text probe reached the correct endpoint but failed with `detected_unusual_activity`.
- Previous ElevenLabs message: Free Tier access is disabled for the account; upgrade to a paid subscription to continue.
- Latest retest with the newest key succeeded for 980 studio files, then stopped because the account exhausted free quota with `quota_exceeded`.

Interpretation:

- The ElevenLabs adapter is structurally correct.
- The current blocker is free quota, not request format.
- ElevenLabs `scribe_v2` is the strongest partial result so far, but needs paid/quota-stable access before it can replace OpenAI for a full pipeline.

Resume command after fixing key permission:

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider elevenlabs --model scribe_v2 --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vie --limit 0 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_full_asr_eval_elevenlabs_scribe_v2.csv --output-jsonl outputs\studio_full_asr_eval_elevenlabs_scribe_v2.jsonl
```

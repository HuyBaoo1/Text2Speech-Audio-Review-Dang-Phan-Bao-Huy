# iFLYTEK Studio 1200 Evaluation Result

## Scope

- Dataset: `audio_samples/studio`
- Ground truth: `data/ground_truth_studio`
- Provider/model: `iflytek:iat-niche`
- Limit: first `1200` studio audio files with ground truth
- Output CSV: `outputs/studio_1200_asr_eval_iflytek_iat_niche.csv`
- Output JSONL: `outputs/studio_1200_asr_eval_iflytek_iat_niche.jsonl`

## Result

- Attempted rows: `1200`
- Successful transcripts: `0`
- Scored rows: `0`
- Error rows: `1200`
- Empty hypotheses: `1200`
- WER/CER: not available because all requests failed at API authentication.
- Follow-up probe after trimming whitespace from `.env` credentials: still failed with the same `401` error.

## Failure Reason

- iFLYTEK returned `401 Unauthorized` during WebSocket handshake.
- Main error message: `HMAC signature cannot be verified: apikey not found`.
- This usually means the configured iFLYTEK `APIKey` is not recognized for the selected service endpoint, or the key is from a different iFLYTEK service/app.

## Recommended Fix

- Verify that `.env` uses credentials from the same iFLYTEK app/service:
  - `IFLYTEK_APP_ID`
  - `IFLYTEK_API_KEY`
  - `IFLYTEK_API_SECRET`
- For Vietnamese/small-language ASR, keep:
  - `IFLYTEK_LANGUAGE=vi`
  - `IFLYTEK_HOST_URL=wss://iat-niche-api.xfyun.cn/v2/iat`
- If your key is for normal Chinese/English Short Form ASR only, use the normal endpoint instead:
  - `IFLYTEK_HOST_URL=wss://iat-api.xfyun.cn/v2/iat`
  - and set a supported language for that service.

## Resume Command

After fixing `.env`, rerun the same command. Existing error rows will be retried because `--resume` only skips successful rows.

```powershell
python scripts\run_asr_evaluation.py --folder audio_samples\studio --provider iflytek --model iat-niche --ground-truth data\ground_truth_studio --quality-csv outputs\studio_full_quality_report.csv --language vi --limit 1200 --only-ground-truth --resume --checkpoint-every 10 --output-csv outputs\studio_1200_asr_eval_iflytek_iat_niche.csv --output-jsonl outputs\studio_1200_asr_eval_iflytek_iat_niche.jsonl
```

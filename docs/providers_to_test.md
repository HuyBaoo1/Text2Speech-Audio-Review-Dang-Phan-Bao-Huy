# Providers To Test

Priority is free/local first, then free-quota hosted APIs.

## Free Local

### VinAI PhoWhisper Small

- Provider in this project: `local-whisper`
- Model: `vinai/PhoWhisper-small`
- Best use: Vietnamese baseline against the current 11 ground-truth clips.
- Cost: free, but requires local compute and model download.

Command:

```bash
python scripts/run_asr_evaluation.py --provider local-whisper --model vinai/PhoWhisper-small --limit 11 --output-csv outputs/asr_eval_phowhisper_small_11.csv
```

## Hosted Free-Quota

### Groq Whisper Large V3 Turbo

- Provider in this project: `groq`
- Model: `whisper-large-v3-turbo`
- Env key: `GROQ_API_KEY`
- Best use: fast Whisper-family hosted baseline.

Command:

```bash
python scripts/run_asr_evaluation.py --provider groq --model whisper-large-v3-turbo --limit 100 --output-csv outputs/asr_eval_groq_whisper_large_v3_turbo.csv
```

### Deepgram Nova-3

- Provider in this project: `deepgram`
- Model: `nova-3`
- Env key: `DEEPGRAM_API_KEY`
- Language default: `vi`
- Best use: production ASR API comparison against OpenAI and Groq.

Command:

```bash
python scripts/run_asr_evaluation.py --provider deepgram --model nova-3 --language vi --limit 100 --output-csv outputs/asr_eval_deepgram_nova3.csv
```

### Gemini 2.5 Flash

- Provider in this project: `gemini`
- Model: `gemini-2.5-flash`
- Env key: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- Best use: free-tier multimodal baseline on the ground-truth subset.

Command:

```bash
python scripts/run_asr_evaluation.py --provider gemini --model gemini-2.5-flash --language Vietnamese --limit 11 --output-csv outputs/asr_eval_gemini_2_5_flash.csv
```

### ElevenLabs Scribe

- Provider in this project: `elevenlabs`
- Model: `scribe_v2`
- Env key: `ELEVENLABS_API_KEY` or `XI_API_KEY`
- Language: `vie`

Command:

```bash
python scripts/run_asr_evaluation.py --provider elevenlabs --model scribe_v2 --language vie --limit 100 --output-csv outputs/asr_eval_elevenlabs_scribe_v2.csv
```

### Azure Speech

- Provider in this project: `azure`
- Model placeholder: `azure-short-audio`
- Env keys: `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`
- Language: `vi-VN`

Command:

```bash
python scripts/run_asr_evaluation.py --provider azure --model azure-short-audio --language vi-VN --limit 100 --output-csv outputs/asr_eval_azure_speech_vi_vn.csv
```

## Suggested Order

1. Run `vinai/PhoWhisper-small` on 11 ground-truth clips.
2. Score it offline with `score_existing_asr.py`.
3. Add Groq key and run `whisper-large-v3-turbo` on 100 clips.
4. Add Deepgram key and run `nova-3` on 100 clips.
5. Add Gemini/ElevenLabs/Azure keys if free quota is available.
6. Compare scored rows where ground truth exists before spending more quota.

Or run the free-quota benchmark runner:

```bash
python scripts/run_free_vi_benchmark.py
```

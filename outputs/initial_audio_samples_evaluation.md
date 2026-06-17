# Initial ASR Evaluation on audio_samples/matched_audio

## Scope

- Audio folder: `audio_samples/matched_audio`
- Total WAV files discovered: `2277`
- Quality analysis subset: `100` first files
- ASR scored files used: `4` model outputs
- Common comparable subset across all scored models: `11` files

## Audio Quality

- Quality gate pass: `50/100`
- Quality gate review: `50/100`
- Duration avg/min/max: `16.08s / 3.24s / 30.00s`
- SNR avg: `46.13 dB`
- Silence ratio avg: `0.296`

## Model Ranking by Own Scored Subset

| Rank | Provider | Model | Rows | WER mean | WER median | WER p95 | CER mean | CER median | Empty hyp |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `openai` | `gpt-4o-mini-transcribe` | 29 | 0.2044 | 0.1897 | 0.4375 | 0.1295 | 0.0810 | 0 |
| 2 | `groq` | `whisper-large-v3-turbo` | 29 | 0.2234 | 0.1910 | 0.4375 | 0.1158 | 0.0892 | 0 |
| 3 | `deepgram` | `nova-3` | 29 | 0.2982 | 0.2131 | 1.0000 | 0.2010 | 0.1093 | 2 |
| 4 | `local-whisper` | `vinai/PhoWhisper-small` | 11 | 0.4317 | 0.4375 | 0.9200 | 0.2207 | 0.1885 | 0 |

## Fair Ranking on Common Subset

| Rank | Provider | Model | Rows | WER mean | WER median | CER mean | CER median |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `openai` | `gpt-4o-mini-transcribe` | 11 | 0.2878 | 0.2759 | 0.1842 | 0.1884 |
| 2 | `groq` | `whisper-large-v3-turbo` | 11 | 0.3077 | 0.2821 | 0.1841 | 0.1748 |
| 3 | `local-whisper` | `vinai/PhoWhisper-small` | 11 | 0.4317 | 0.4375 | 0.2207 | 0.1885 |
| 4 | `deepgram` | `nova-3` | 11 | 0.4700 | 0.4242 | 0.3531 | 0.2424 |

## Interpretation

- Best current model on its scored subset is `openai:gpt-4o-mini-transcribe` with WER mean `0.2044` and CER mean `0.1295`.
- On the common subset, best current model is `openai:gpt-4o-mini-transcribe` with WER mean `0.2878` and CER mean `0.1842`.
- The current benchmark is still small for final model selection because only files with manual ground truth can be scored.
- For car AI use, the next dataset slice should add command-like Vietnamese/English code-switch utterances and noisy in-cabin audio.
- Do not choose a production ASR model from WER alone; add intent accuracy, slot F1, p95 latency, error rate, and cost per hour.

## Artifacts

- `outputs/initial_audio_samples_model_summary.csv`
- `outputs/initial_audio_samples_common_subset_summary.csv`
- `outputs/quality_report.csv`
- Existing provider scored CSVs under `outputs/asr_eval_*_scored.csv`

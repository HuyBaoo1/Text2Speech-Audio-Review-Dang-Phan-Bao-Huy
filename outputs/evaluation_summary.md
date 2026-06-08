# Evaluation Summary

## Dataset

- Source folder: `audio_samples/matched_audio`
- Evaluated sample count: `100`
- Ground truth matched for ASR scoring: `11`

## Audio Quality

- Quality gate pass: `50`
- Quality gate review: `50`
- Average duration: `16.08s`
- Min duration: `3.24s`
- Max duration: `30.00s`
- Average SNR: `46.13 dB`

## OpenAI ASR Result

- Provider/model: `openai:gpt-4o-mini-transcribe`
- Average WER on ground truth subset: `0.2878`
- Average CER on ground truth subset: `0.1842`
- Best WER: `0.0625`
- Worst WER: `0.6400`

## Scored Files

| file | WER | CER | duration | quality_gate |
| --- | ---: | ---: | ---: | --- |
| `-Yg0ClzBn2k_143.wav` | 0.0625 | 0.0417 | 6.893 | False |
| `-aCDck13cRI_30.wav` | 0.0986 | 0.0762 | 13.226 | True |
| `-Yg0ClzBn2k_0.wav` | 0.1639 | 0.0565 | 13.430 | True |
| `-aCDck13cRI_39.wav` | 0.1923 | 0.0802 | 19.643 | True |
| `-Yg0ClzBn2k_69.wav` | 0.2727 | 0.1923 | 14.703 | True |
| `-Yg0ClzBn2k_93.wav` | 0.2759 | 0.1230 | 5.925 | True |
| `-Yg0ClzBn2k_35.wav` | 0.3182 | 0.2019 | 4.516 | True |
| `-Yg0ClzBn2k_40.wav` | 0.3514 | 0.2656 | 15.790 | False |
| `-Yg0ClzBn2k_48.wav` | 0.3529 | 0.1884 | 3.633 | False |
| `-aCDck13cRI_14.wav` | 0.4375 | 0.3182 | 3.854 | True |
| `-Yg0ClzBn2k_62.wav` | 0.6400 | 0.4828 | 7.385 | False |

## Interpretation

- 50/100 clips pass the current automatic quality gate; the other 50 should be manually reviewed or segmented/trimmed.
- OpenAI ASR is usable as a bootstrap transcript source, but the current ground truth subset still shows meaningful error variance.
- The worst current file is a good candidate for manual error tagging before trusting bulk transcription.
- Local open-source ASR should be run next on the same 11 ground-truth files first, then expanded to 100 if runtime is acceptable.

## Artifacts

- `outputs/quality_report.csv`
- `outputs/asr_eval_openai.csv`
- `outputs/asr_eval_openai_scored.csv`
- `outputs/asr_eval_openai_scored.jsonl`

# Imported Ground Truth

Ground truth imported from Google Sheets for a future dataset batch.

Source:

```text
https://docs.google.com/spreadsheets/d/1DxWbnP1QLKmalj1zvwyFp1I3bIr0sa2wi4So2y4SGiA/edit?gid=182648600
```

Files:

| File | Purpose |
| --- | --- |
| `google_sheet_1DxWbnP1QLKmalj1zvwyFp1I3bIr0sa2wi4So2y4SGiA_gid182648600_raw.csv` | Raw CSV export from Google Sheets. |
| `omni_vi_ai_ground_truth.csv` | Normalized ground truth for pipeline use. |
| `omni_vi_ai_ground_truth_metadata.json` | Import metadata and validation counts. |

Normalized schema:

| Column | Meaning |
| --- | --- |
| `audio_file` | Expected audio file name, derived from `audio_stem + ".wav"`. |
| `audio_stem` | Audio id from the sheet. |
| `reference_text` | Reconstructed transcript text. |
| `source_sheet_id` | Google Sheet id. |
| `source_gid` | Google Sheet tab id. |
| `source_row` | 1-based source row in the exported CSV. |

Import notes:

- The exported sheet has no explicit header row.
- Each raw row starts with `audio_stem|first_text`.
- Remaining non-empty CSV cells are continuation transcript segments.
- `reference_text` is reconstructed by joining all non-empty transcript segments with `, `.

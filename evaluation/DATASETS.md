# Dataset manifest

| File | Role and provenance |
|---|---|
| `data/raw/boulder_ev_charging_data.csv` | 5,000 generated Indian sessions. Contains Noida, Greater Noida, New Delhi and Gurugram. The historical filename is retained for existing code paths. |
| `data/processed/cleaned_sessions.csv` | Derived features and model inputs for the saved local benchmark. |
| `data/streaming/live_stream_buffer.jsonl` | Simulated event fixture with Boulder-labelled station names, replayed independently of the Indian sessions and public station directory. |
| `src/web/stations.js` | Bundled Open Charge Map India station snapshot used by the website. Source is the Open Charge Map India export. |
| `data/processed/model_metrics.json` | Saved scikit-learn benchmark output, used by the offline BI scorecard. |
| `data/processed/plots/` | Saved outputs for results discussion and fallback presentation. |

The primary session experiment uses generated data. Confirm that your faculty accepts this dataset for assessment. Map locations and published grid figures are independent contextual sources.

The cleaned CSV is the historical benchmark input. It preserves the original weekday encoding, including day 0. The ETL source now uses the Spark day convention in both branches. Regenerating the cleaned CSV can change weekend flags and model scores.

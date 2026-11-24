# VoltPulse live demonstration run sheet

## 10–12 minute flow

| Time | Action and talking point |
|---|---|
| 0:00–1:30 | Introduce VoltPulse and the three decisions it supports. Distinguish the public directory, the synthetic sessions and the replay fixture. |
| 1:30–3:00 | Walk through the architecture. Point to the raw CSV, prepared CSV, two trainer entry points and saved scorecard. |
| 3:00–5:00 | Open the portal. Search for Noida or another known city, inspect a station record and discuss connector and access checks. Show a trip route if network services respond. |
| 5:00–6:30 | Open the offline BI page. Filter to Noida and DC Fast. Explain that the headline KPIs and hour counts respond to the filters. |
| 6:30–8:30 | Show the terminal output from Spark ETL and MLlib if the run has completed. Discuss the saved benchmark separately. The Random Forest energy RMSE was 7.9241 kWh on the benchmark split. |
| 8:30–9:30 | Replay the saved JSONL. Explain that its aggregate sums event power readings and that the threshold is per event. |
| 9:30–11:00 | Cover Parth Vij's listed contribution and SDGs 7, 11 and 13. Explain what measured evidence would be needed before making operational claims. |

## Start from the repository root

```powershell
python --version
java -version
python -m pip install -r requirements.txt
python src/web/server.py
```

Open http://localhost:3000. For a local preview with Node and no Python, run `node evaluation/serve-demo.mjs` instead.

In another terminal:

```powershell
python src/etl/etl_pipeline.py
python src/models/train_pyspark_mllib.py
python src/ingestion/spark_stream_consumer.py
```

The ETL has a portable fallback. Check for the explicit Spark success message. The MLlib script prints metrics. Run the scikit-learn trainer separately only when intentionally refreshing the saved benchmark. Have the offline dashboard, saved charts and the replay evidence file open before presenting.

## Short viva answers

- **Where is Spark used?** The Spark SQL ETL branch and the native MLlib training script. Replay is a Python file aggregation.
- **Is this grid forecasting?** The saved energy task estimates session kWh using session features, including active duration. A next-hour feeder forecast would need time-series and feeder telemetry.
- **Why is classification F1 high?** Hour defines the synthetic target and is included among the model inputs. The model learns the hour rule. Observed queue length is a future target.
- **What does a centroid mean?** It summarises coordinates assigned to a cluster. A viable site needs checks for grid capacity, demand, road access and land.
- **How do the SDGs connect?** SDG 7 through energy visibility, SDG 11 through spatial access, and SDG 13 through support for electrified trip planning. Emissions reduction was not measured.

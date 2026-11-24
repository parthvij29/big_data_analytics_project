# VoltPulse

VoltPulse helps EV drivers find mapped charging stations, estimate a charge and plan a road trip in India. The municipal workspace explores the same directory by city. The grid workspace links published Indian electricity demand figures to their source.

## Run the website

From the repository root, run `python src/web/server.py` and open http://localhost:3000. The website can also be served by a static host. GPS requires localhost or HTTPS.

Station coordinates and connector details come from the [Open Charge Map India export](https://github.com/openchargemap/ocm-export/tree/main/data/IN). The directory is a snapshot. Individual records may be incomplete or out of date. City lookup, routing and map tiles require internet access. The route calculator uses the driving range entered by the driver. Suggested charging areas require a check of connector compatibility and access.

## Analytics and reports

The [session generator](src/etl/generate_sample_dataset.py) produces synthetic charging sessions. Despite its historical filename, `data/raw/boulder_ev_charging_data.csv` contains simulated Indian sessions. The website uses separate sources for displayed station locations and national demand.

From the repository root, with Python 3.11 and a Spark-compatible JDK (Java 17 recommended for Spark 3.5), run:

```powershell
python -m pip install -r requirements.txt
python src/etl/etl_pipeline.py
python src/models/train_pyspark_mllib.py
python src/models/train_all_models.py
python src/dashboard/generate_plots.py
python src/ingestion/spark_stream_consumer.py
```

Look for the explicit Spark success message before presenting the ETL as a Spark run. The ETL can fall back to Python and still write the cleaned CSV. The MLlib trainer prints its metrics to the terminal. The separate scikit-learn trainer writes `data/processed/model_metrics.json`. Session-energy predictions use active charging duration as a feature. Congestion labels are generated from the hour of day. The streaming consumer reads a saved simulated JSONL event buffer.

`PROJECT_DESC.md`, `docs/PROJECT_SPEC.md` and the Milestone 1 report preserve the earlier design. The evaluation report and dataset manifest describe the submitted data and current implementation.

Open [the evaluation guide](evaluation/START_HERE.md) for the package, demo sequence, and outstanding verification.

[Project description](PROJECT_DESC.md) · [Milestone report](report/VoltPulse_Milestone1_Report.docx)

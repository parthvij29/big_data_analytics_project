# VoltPulse

VoltPulse helps EV drivers find mapped charging stations, estimate a charge and plan a road trip in India. The municipal workspace explores the same directory by city. The grid workspace links published Indian electricity demand figures to their source.

## Run the website

From the repository root, run `python src/web/server.py` and open http://localhost:3000. The website can also be served by a static host. GPS requires localhost or HTTPS.

Station coordinates and connector details come from the [Open Charge Map India export](https://github.com/openchargemap/ocm-export/tree/main/data/IN). The directory is a snapshot. Individual records may be incomplete or out of date. City lookup, routing and map tiles require internet access. The route calculator uses the driving range entered by the driver. Suggested charging areas require a check of connector compatibility and access.

## Analytics and reports

The [session generator](src/etl/generate_sample_dataset.py) produces synthetic charging sessions. The ETL, streaming and training code under `src/` uses these project artifacts for experimentation. The website uses separate sources for displayed station locations and national demand.

[Project description](PROJECT_DESC.md) · [Milestone report](report/VoltPulse_Milestone1_Report.docx)

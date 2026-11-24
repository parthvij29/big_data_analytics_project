# VoltPulse evaluation package

## Open these first

- [Final report draft](VoltPulse_Final_Report.docx) contains Chapters 1–5 and supporting appendices. The [PDF](VoltPulse_Final_Report.pdf) provides fixed pagination. Review the faculty line, declaration and signatures before uploading.
- [Presentation](VoltPulse_Presentation.pptx) is editable. The [offline browser copy](VoltPulse_Presentation.html) works with the arrow keys.
- [Experiment BI dashboard](VoltPulse_BI.html) runs offline and filters by city and connector. The dashboard is the BI deliverable. The Power BI build guide is included in the source documentation.
- [Live demo run sheet](DEMO.md) gives commands, timings, talking points and fallback evidence.
- [Dataset manifest](DATASETS.md) describes the source, processed dataset, simulated replay and public charger directory.
- [Saved results](../data/processed/plots) include the model comparison, hourly profile and clustering plots. [BI screenshot](BI-screenshot.png) and [portal screenshot](Portal-screenshot.png) were captured in Chrome. [Python run evidence](python-run-evidence.txt) records the portable ETL check and live replay of the saved JSONL fixture.

## Before the evaluation on 25 November 2026

1. Start the website and rehearse one station query and one BI filter. Confirm external tiles and routing on the evaluation network.
2. Run the native PySpark ETL and five-model MLlib trainer. Capture the success signal and actual metrics, then add a screenshot of the Spark run. The existing scorecard presents saved scikit-learn results.
3. Confirm faculty approval for the synthetic dataset. The raw CSV has the historical Boulder filename and contains simulated Indian sessions. The separate simulated replay uses Boulder station labels.
4. In Word, check the prescribed layout, page numbers and faculty details. Confirm that the declaration accurately describes the final report and that any assistance has been handled under course rules before signing.
5. Use the university Turnitin workflow, record the verified scores and include the exported report. Table 2 specifies below 10% similarity for full marks and a 0% AI score. This package contains no measured Turnitin score.
6. Upload the required report, source, data, results screenshots and Turnitin report before the corrected morning deadline. Upload fields vary by course. Keep the deck ready for the live evaluation.

The report allocates 50 numbered pages to Chapters 1–5, with the prescribed chapter ranges. Front matter, references and appendices are separate. Word may repaginate on a different workstation. The supplied Milestone 1 document is retained in the repository as an earlier version.

The local portal returned HTTP 200. The BI test showed 5,000 sessions across all cities, 1,717 sessions for Noida, and 1,236 with both Noida and DC Fast selected. The Python ETL fallback processed all 5,000 rows, and the replay produced 37 occupied event rows and two readings over 45 kW. PySpark was unavailable in this environment.

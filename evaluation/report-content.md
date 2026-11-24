# 1 Problem Domain Identification and Analysis
## 1.1 Background of the Study
A charging session ties together three quantities that are easy to confuse: the time a vehicle occupies a bay, the time it draws energy, and the total energy delivered. A vehicle can occupy the bay after charging stops. As a result, energy throughput and bay utilisation describe different operational constraints. VoltPulse treats both as relevant to station planning.
The project combines a browser-based Indian charger directory with a separately reproducible analytics experiment. The directory is intended for discovery and approximate travel planning. The experiment uses simulated sessions to investigate data preparation, model evaluation and the interpretation of charging patterns. Each result is presented with its source and unit.
## 1.2 Introduction to the Problem Domain
Drivers need to find equipment compatible with their vehicles and identify locations within driving range. Operators need to distinguish high average session demand from concurrent power draw. Municipal planners need to understand where mapped equipment is concentrated and where additional evidence would be needed before proposing a site.
Electric energy is measured in kWh and power in kW. Dividing session energy by active charging time gives average session power. Measuring the simultaneous load of several chargers requires timestamped readings or a validated model of overlapping sessions. This distinction determines which conclusions can be drawn from the available tables.
## 1.3 Literature Review
Lee, Li and Low describe ACN-Data, an open collection of measured workplace charging sessions. Their examples include analysing driver behaviour, sizing on-site solar generation and using workplace charging to smooth net demand [1]. Session logs can therefore support useful studies when the collection context is understood.
Apache Spark MLlib provides a DataFrame-based interface for feature transformation, training and evaluation [2]. Open Charge Map provides a geographically indexed directory, which is a different kind of evidence from charging-session telemetry [3]. VoltPulse uses the directory for location discovery. ACN-Data informs the literature review.
## 1.4 Research Gap and Literature Gaps
Real session datasets, station directories and national electricity publications answer different questions. A location record describes the existence and attributes of mapped equipment. A session log describes charging behaviour at sampled sites. A national demand figure describes aggregated electricity demand at its reporting scale.
The gap addressed here is how these sources can be displayed and interpreted together while keeping their provenance visible. There is no shared live station identifier across the current datasets. Linking a predicted session to a mapped charger would require persistent station and port identifiers, source dates and quality checks.
## 1.5 Review of Existing Solutions
A charging directory helps a traveller locate compatible equipment. Its usefulness depends on coverage and the completeness of operator or contributor updates. A measured-session repository can support detailed charging analysis, but its station sample reflects the geography and user population from which it was collected.
A utility dashboard usually uses feeder or system-level demand at a defined reporting interval. The current VoltPulse grid workspace links published Indian demand measures to their source. The experiment estimates session energy and active duration independently from those published measures.
## 1.6 Limitations of Existing Systems
A static directory can list a charger whose access restrictions, hours or connector status have changed. Historical records can also underrepresent driver populations or locations. Model accuracy derived from a particular charger mix and time period may change when those conditions change.
The same concerns apply to this prototype. The offline experiment allows repeatable comparisons, but its synthetic assumptions shape the hour profile and label distribution. The application can support exploration and the formulation of hypotheses for field validation.
## 1.7 Problem Statement
Build an EV charging prototype that exposes an Indian station directory and evaluates methods for deriving decision-support indicators from session records. The experiment compares two estimators of energy delivered per session, classifies a time-based congestion proxy, estimates active charging duration and groups station coordinates.
The implementation should preserve the distinction between modelled electricity use, simulated telemetry and independently published electricity demand. A reproducible demonstration should make it possible to trace each output back to the corresponding script, input or public source.
## 1.8 Proposed Solution Overview
The source tree includes a generator, an ETL pipeline, two model training entry points, a telemetry replay, a static website and an evaluation dashboard. The generator and training data support experimentation. The website focuses on finding stations, estimating charging needs and exploring city coverage.
The assessment dashboard displays the experiment's session counts, energy measures and model evidence. The map and this dashboard serve different decisions. The architecture keeps file interfaces explicit so that new session data can be analysed before any integration with the station directory is attempted.
## 1.9 Objectives of the Project
Prepare structured session features from a reproducible dataset. Compare five estimators across regression, classification and clustering. Demonstrate the aggregation of simulated telemetry and present analytical outputs with their units and limitations.
Provide a driver view for map and trip exploration, a municipal view for coverage and a grid view for source-linked context. Explain how the prototype relates to SDGs 7, 11 and 13 using measurable outcomes that a future deployment could evaluate.
## 1.10 Scope of the Project
The analytical sample contains 5,000 generated Indian charging sessions and a separate saved telemetry sample that uses Boulder station names. The web directory represents an Open Charge Map snapshot. The evaluation covers local execution and source inspection.
The project scope excludes production charger control, measured queue prediction, transformer protection and measured emissions reduction. Before using outputs in operations, a deployment would need authenticated feeds, an explicit prediction horizon, appropriate evaluation splits and authorisation to use operational data.
## 1.11 Industrial Applications and Use Cases
Charge point operators could use measured duration and energy summaries for maintenance and capacity reviews. Fleet coordinators could compare route options and charging buffers. A city analyst could filter station locations by city and use coverage maps to decide where to collect additional data.
Each use case has a separate acceptance criterion. Trip planning needs usable connector and access details. Site planning needs travel demand, coverage and grid feasibility evidence. Utility applications need validated telemetry and explicit operational thresholds.
# 2 Project Design and Methodology
## 2.1 System Overview
The prototype has two entry points. The website serves the directory and planning tools. The analytics scripts read session data, compute features and produce results for the evaluation dashboard. The demonstration runs these entry points independently.
An evaluator can follow one session from a CSV row into the feature table, then into a regression or classification run. In the separate browser demonstration, an evaluator can select a city and inspect station and connector information.
## 2.2 Proposed System Architecture
The offline path starts at the synthetic CSV. ETL produces the cleaned CSV for the local benchmark and the evaluation views. The native MLlib trainer independently reads the raw CSV and derives its own features. The replay reads saved JSONL events and produces a console summary.
The online-facing path starts at the bundled Open Charge Map station snapshot. The browser handles rendering and user input. Map tiles, geocoding and route queries use external services. National electricity context is sourced separately.
## 2.3 Architecture Components and Their Functions
The generator defines the synthetic session distribution. ETL converts source fields into numeric and temporal features. The two trainers implement comparable model families with backend-specific configuration. The plotting script consumes the benchmark data and emits result images.
The telemetry generator appends to a local JSONL file. The repository consumer scans JSONL in a single pass. The producer's Kafka-oriented filename reflects the original design. The web server delivers static assets. The evaluation dashboard is built from the supplied experiment artifacts and stays usable without a network connection.
## 2.4 Proposed Methodology
The project follows an iterative analytical process: establish stakeholder questions, inventory sources, prepare data, train model families, evaluate each task and communicate results. Source checks occur before modelling because source errors affect every downstream conclusion.
The current evaluation uses a seeded random holdout for supervised benchmark tasks and an in-sample clustering measure. A subsequent operational evaluation would isolate later dates and unseen stations to measure generalisation across time and geography.
## 2.5 Methodology Workflow Use Case and DFD Flow Diagram
For session modelling, the external entity is the dataset generator. It supplies session rows to feature preparation, which writes a cleaned table. The benchmark reads the cleaned table and produces metrics, plots and centroids. The evaluator reads those outputs in the dashboard and report.
For the discovery use case, the driver supplies a city or trip inputs. The website finds relevant station records and can request external routing. The planner filters mapped locations. The grid workspace presents published aggregates as context.
## 2.6 Algorithms and Techniques Used
Gradient boosting adds decision trees sequentially to improve predictions against a loss function. Random forests combine decision trees trained with randomisation. The energy regressors use the same held-out population in the benchmark so that a difference in error can be interpreted within that experiment.
Random forest classification estimates three time-derived categories. Linear regression fits active duration as a function of energy, hour, connector class and weekend status. K-means allocates coordinate pairs to four clusters and recomputes cluster centroids.
## 2.7 Dataset Description
The experiment uses 5,000 generated sessions across Noida, Greater Noida, New Delhi and Gurugram. The raw CSV has 17 columns for station identity, address, coordinates, timestamps, duration, energy, connector family, port and generated user identifier.
The filename retains the earlier Boulder naming convention. The individual sessions are simulated and should be attributed to the repository generator. Faculty acceptance of the synthetic dataset is unconfirmed. The website's station snapshot and the separate Boulder-labelled simulated replay have their own provenance.
## 2.8 Data Collection and Data Preprocessing
Time parsing derives hour, day of week and weekend status. The DC fast indicator is a binary encoding of port type. Energy and duration are expressed in kWh and minutes. Congestion labels 0, 1 and 2 refer to low, moderate and high proxy categories.
Peak classes are produced by the same hour field later given to the classifier. A high score shows that the model learned a deterministic time rule on these inputs. It does not establish accuracy on recorded queue lengths. Future occupancy labels would need a direct observational source.
## 2.9 Tools and Technologies Used
The implementation uses Python, PySpark SQL and MLlib, pandas and scikit-learn, Matplotlib, a static browser interface, and JSONL and CSV storage. Spark is the intended distributed batch engine. Kafka is a potential transport for replacing local JSONL in a future deployment.
The repository contains a Power BI build guide. This submission adds a browser BI view based on the supplied data and result artifacts. Its filters and measures operate over the simulated sessions. An editable Power BI project would be a separate integration artifact.
## 2.10 Experimental Setup and Configuration
The benchmark uses a test fraction of 0.2 and a seed of 42. The two energy models use the same split. The benchmark uses four geographic clusters and deduplicates latitude and longitude before fitting them.
The native Spark script uses local mode and its own seeded random splits. It prints Spark evaluation metrics. The saved JSON metrics shown in this report come from the benchmark entry point, whose settings and evaluation implementation are distinct from MLlib.
## 2.11 Evaluation Metrics
RMSE and MAE report error in the target's units. R squared measures fit relative to a mean-prediction baseline. On the energy task the units are kWh. On duration the units are minutes. Scores across different targets answer different questions.
Accuracy and weighted F1 summarise proxy classification. Class-specific errors would require a confusion matrix. Silhouette compares within-cluster cohesion with separation from other clusters. Inertia measures squared Euclidean spread and tends to decline as more clusters are introduced.
# 3 Project Implementation
## 3.1 Development Environment
The web interface can be served with the standard-library HTTP server in the repository. Python 3.11 and Java 17 are a practical setup for Spark 3.5. Package installation and version records should be checked on the evaluation workstation before running the native trainer.
The packaged HTML BI evidence can be opened directly from disk. This reduces dependence on external services when presenting the session results. The source distribution includes the data, scripts, dependency list and directory assets.
## 3.2 System Implementation Overview
The operational sequence begins by confirming the raw file identity, then running ETL and either model path. The local benchmark writes JSON. The plot generator reads experiment inputs and emits images. The independent web process serves the driver-facing and planner-facing pages.
The project has a single root from which the Python entry points resolve relative paths. Keeping that working directory consistent avoids a missing-file error even when the scripts are opened from multiple locations.
## 3.3 Module Description
The ETL module owns column construction. The modelling modules own training and evaluation. The ingestion modules produce and aggregate simulated events. The website contains its own server, styles, scripts and station directory.
This division makes troubleshooting direct. A data conversion problem should be investigated in ETL. A missing Java process belongs to Spark setup. Missing map tiles require checking the network and provider. The output has separate file paths for each of these concerns.
## 3.4 Data Processing and Implementation
Spark reads the CSV and builds feature columns through DataFrame expressions. A portable CSV fallback provides the same basic feature families. The terminal message identifies the processing branch. The historical CSV has day-of-week values 0 through 6. Both branches now use Spark's 1 through 7 convention. Reruns can therefore change weekend flags and benchmark inputs.
The Spark branch converts its processed result to a pandas frame before writing a single CSV. That export is convenient at the submitted scale. A larger deployment should write partitioned files directly from Spark and avoid collecting the entire result at the driver.
## 3.5 Algorithm Implementation
The benchmark code constructs separate feature matrices for energy, congestion and duration. The energy estimators share a split. The linear model uses observed session energy. The classification feature set includes hour, which defines the target categories.
The MLlib code uses VectorAssembler and Spark estimators and evaluates regression, classification and clustering in the Spark session. Its cluster inputs include repeated session coordinates, unlike the deduplicated benchmark. The corresponding silhouette measures should not be compared without aligning preprocessing and evaluator settings.
## 3.6 Database or Storage Implementation
Raw and processed CSVs hold tabular experiment data, JSONL holds recorded simulated messages, and JSON holds the benchmark output. The station directory is shipped as a JavaScript asset for browser use.
The repository also includes a SQL file for optional contact-message storage. Core analytics and the evaluation dashboard run independently of that backend. The project uses files for its submitted experiment artifacts.
## 3.7 Integration of System Modules
The cleaned CSV forms the interface from ETL to the local benchmark and BI. The benchmark JSON supplies the scorecard for the BI view. The native Spark pipeline traces its work to the raw CSV and its own feature logic.
The website's route and directory functions do not call these trainers. Keeping the analytics and website independent lets the operator rehearse the dataset experiment even when routing services are unavailable.
## 3.8 Code Implementation Description
The README lists commands in dependency order. The session generator is available when a new synthetic sample is needed. Re-running generators can overwrite experiment inputs. The supplied data files should remain available so the report's claims can be checked against the same snapshot.
The processing scripts have intermediate console outputs, which help establish whether a Spark run completed. The checked-in benchmark and plots support a fallback walkthrough if a native run cannot complete during the evaluation slot.
## 3.9 System Interface and Screenshots
The browser implements a public-facing station interface. The evaluation dashboard adds city and connector selectors and computes measures from the provided session data. Its model scorecard uses saved benchmark metrics with a backend label.
Appendix A contains supplied result images and experiment evidence. A live examiner can verify the website independently by opening the local server and interacting with the directory and planning controls.
## 3.10 Limitations of the Implementation
The telemetry consumer aggregates records from a saved file and applies an event-level threshold. It does not measure actual feeder headroom or calculate watermarked Spark windows. The portal's published demand context does not serve as ground truth for the batch models.
Training is offline. Spark scaling has not been benchmarked across multiple hosts, and the session data are synthetic. The browser may need connectivity for mapping and routing, while the assessment dashboard can be opened offline.
## 3.10.1 Reproduction Checks
Check the source row count before running ETL and compare it to the number of prepared rows. For a sample row, compute hour and day of week directly from the timestamp. Confirm that Saturday and Sunday enter the weekend group and that connector names map to the expected indicator.
For a native benchmark, record the Python, JVM and Spark versions and the exact input files. Preserve the console messages from the ETL branch and MLlib trainer. These records can explain discrepancies caused by backend differences, changed features or modified data.
When testing the application, check that the station view shows connector details for a known city. Apply the same city to the BI view and compare its synthetic session counts to the input data. The map count and experimental session count measure different populations.
# 4 Project Results and Discussion
## 4.1 Experimental Setup
The results in this chapter are drawn from the supplied CSV data, benchmark JSON, stored plot images and a deterministic read of the telemetry buffer. The model metrics describe the scikit-learn benchmark. The evaluation dashboard reads these artifacts at package generation time.
Regression and classification hold out one fifth of the data with a fixed seed. K-means is fit on deduplicated coordinate pairs for the saved benchmark. The available evidence does not include a newly executed Spark scorecard.
## 4.2 Experimental Scenarios
The first scenario compares two energy regressors on a shared split. The second classifies the time-based congestion proxy. The third estimates active charging duration from observed energy and other features. The fourth clusters station coordinates.
The replay scenario aggregates a fixed event fixture and identifies records over 45 kW. The UI scenario demonstrates the distinction between the public station map and the experimental session dashboard. These scenarios exercise different inputs and expected outputs.
## 4.3 Output Results
The Random Forest energy benchmark produced an RMSE of 7.9241 kWh. The gradient-boosted energy benchmark produced 8.0874 kWh. Active-duration regression reached an RMSE of 23.9893 minutes and MAE of 16.8761 minutes.
The random forest classifier reached accuracy 0.9630 and weighted F1 0.9620 on time-derived labels. Four coordinate clusters gave a silhouette of 0.4445. These results describe the submitted synthetic sample and its saved model outputs.
## 4.4 Performance Evaluation
The Random Forest had lower errors on the saved energy split, but the RMSE difference was only 0.1633 kWh. There is no repeated-run distribution in the supplied metrics. An estimate of uncertainty would need repeated splits, a temporal test, or a station-level holdout.
Duration regression's R squared of 0.8237 must be read with its MAE of about 17 minutes. Observed energy is a strong input because active duration is physically related to delivered energy. If energy is unknown before arrival, a separate pre-session estimate and error study would be required.
## 4.5 Comparative Analysis
The two energy regressors are directly comparable on the saved split because they share the same target and feature set. Random Forest has the lower MAE by 0.0913 kWh and higher R squared by 0.0267. A practical next comparison would include a station or connector-based mean predictor.
The duration result, classification F1 and clustering silhouette have different scales and objectives. Although a chart can display them together, their magnitudes do not rank the tasks. The scorecard reports targets and units beside the values.
## 4.6 Evaluation Using Performance Metrics
Weighted precision in the saved classification output is 0.9673 and weighted recall is 0.9630. Hour defines the three class labels, so a deterministic hour rule would reproduce those labels exactly when the timestamps are valid. An operational model would require independent congestion observations.
The geographic model's inertia is 0.0314 in squared coordinate units. Because the experiment uses unprojected latitude and longitude, these units do not express travel distance. Road access and feasible grid connections would have to be tested separately.
## 4.7 Visualization of Results
The saved hourly figure can be used to explore the synthetic activity profile. The model comparison figure provides a compact visual index. The centroid plot visualises a four-group partition of the experiment coordinates.
The offline evaluation dashboard exposes city and connector filters with counts, total energy, mean charging duration and a session-start hour profile. Filters recalculate totals over the selected subset. An hour bin reflects session starts rather than the time at which all energy was transferred.
## 4.8 Discussion and Interpretation
The benchmark establishes a working example of end-to-end analytical evaluation on the submitted sample. Relative performance is most informative when the comparator models share a task and split. Strong proxy classification results are explained by the availability of the very feature that defines the labels.
The dataset's geography and session mix reflect generator design. The prototype can support demonstrations of feature engineering and metric interpretation. Independent measured data are needed for claims about driver behaviour, charging queues or utility performance.
## 4.9 Key Findings
Random Forest performed slightly better than gradient boosting on the saved energy split. Linear regression explained much of the generated variation in active duration but left a material absolute error. The classifier reproduced a synthetic time-of-day rule with high accuracy.
The four geographic centres summarise the station coordinates in the model sample. The directory and dashboard show two different kinds of analytical decision support. The replay fixture shows how to inspect high-power events without claiming a real feeder condition.
# 5 Project Conclusion and Presentation
## 5.1 Project Summary
VoltPulse implements a charger directory and trip planning interface and accompanies it with a batch analytics experiment. The experiment includes session preparation, two energy regressors, one classifier, one duration regressor and coordinate clustering.
The submission provides the source and inputs needed to reproduce the experiment, as well as saved outputs for discussion. The report documents where public, simulated and published contextual inputs enter the system.
## 5.2 Conclusion
The prototype demonstrates how an evaluator can trace an experiment from a session file to model metrics and an interactive BI view. It also shows how a map-based tool can address driver and municipal decisions using a separate location source.
The experimental evidence supports comparison on the submitted sample. Operational forecasts, queue estimates and site investment decisions need a more representative dataset and task-specific validation.
## 5.3 Achievement of Project Objectives
The source contains feature preparation, both modelling implementations, simulated event replay, a website and an offline BI view. The benchmark artifacts include five saved model results. The supplied presentation walks through the evidence and its limits.
The course requires Apache Spark. A successful local run of the native ETL and MLlib path should be demonstrated or supplied as fresh evidence. Faculty acceptance of the generated sessions and the Turnitin checks are separate submission requirements.
## 5.4 Project Limitations
The experiment has synthetic labels, a random split and a simulated station mix. These constraints prevent direct generalisation to a production grid. The clustering result uses geometric proximity and lacks economics, transport flows and feasibility constraints.
Reliability depends on directory freshness and the availability of external map and route services. Faculty approval, authorship declarations and academic integrity results require independent confirmation.
## 5.5 Future Scope and Enhancements
Obtain approved measured charging sessions and stable station identifiers. Define supervised targets that exist at decision time. Create time-based and station-based holdouts and compare against explicit baselines. Attach confidence intervals or repeated-run results.
For streaming work, connect a configured broker and implement event-time windows, watermarks and checkpoints in Spark. For planning, add projected coordinates, road network access, electricity capacity, and demand or equity measures. Validate each addition with observable criteria.
## 5.6 Practical and Industrial Applications
SDG 7 relates to energy-use visibility and evidence-based charging demand management. SDG 11 relates to access to charging infrastructure and better-informed urban siting. SDG 13 relates to mobility electrification, with emissions benefits dependent on energy sources, displaced trips and actual deployment.
A future evaluation can measure delivered energy and peak demand for SDG 7, the share of areas within reach of suitable chargers for SDG 11, and net greenhouse gas emissions under documented assumptions for SDG 13 [4].
## 5.7 Final Remarks
The presentation documents the individual contribution listed in the milestone report and demonstrates the directory, evidence dashboard, replay and benchmark results. Contribution and faculty details should be checked against official records before submission.
The prototype is best assessed by combining the live demonstration with the supplied reproducible artifacts. The report's main conclusions follow from the named data and scripts, and its proposed upgrades describe what evidence remains necessary.
## 5.7.1 Evaluation Presentation and Demonstration
Start with the driver, operator and planner decisions that motivated the two application paths. Demonstrate a station lookup first. Then open the experiment dashboard and filter by a city and connector. Explain the resulting session counts, energy units and time profile before showing the benchmark.
Introduce the Random Forest and gradient boosting comparison on the shared energy split. Explain why classification on hour-derived labels and clustering on coordinates do not predict physical queues or establish suitable sites. Show the recorded telemetry replay and discuss what a measured data source would provide.
Close with the stated contribution and the three SDG links. Use the measurement proposals in Section 5.6 to explain how a pilot could test whether the system helped users, operators or planners make better decisions.

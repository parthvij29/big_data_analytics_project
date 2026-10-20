# VoltPulse: Technical Specifications & Course Rubric Alignment

This document outlines the architectural specifications, dataset schemas, algorithmic formulation, and university milestone deliverables for **VoltPulse**, fulfilling all requirements specified in the Big Data Project Curriculum.

---

## 1. Problem Statement & Research Motivation
The transition to zero-emission mobility has spurred massive deployment of Electric Vehicles (EVs). However, commercial and residential charging infrastructure faces three fundamental bottlenecks:

1. **Grid Instability & Transformer Stress (Utility/Admin Perspective):** Uncoordinated charging peaks overload municipal distribution transformers, causing brownouts and costly peak-demand surcharges.
2. **Charger Anxiety & Bay Blocking (EV Driver Perspective):** Drivers encounter long queues, out-of-order plugs, or unpredicted charging durations, diminishing user experience.
3. **Inefficient Infrastructure Siting (Urban Planning Perspective):** Capital investments often lead to chargers positioned in low-traffic zones while high-demand urban corridors remain "charging deserts".

**VoltPulse** addresses all three challenges concurrently using a distributed Apache Spark data lakehouse, real-time streaming, and PySpark MLlib predictive intelligence.

---

## 2. Authentic Public Datasets
The project utilizes authenticated, open-access city data:
- **Primary Dataset:** **City of Boulder Open Data — Electric Vehicle Charging Station Energy Consumption** (or City of Palo Alto EV Data).
- **Secondary Reference:** **Caltech ACN-Data (Adaptive Charging Network)**.

### Core Schema & Attributes:
| Attribute Name | Data Type | Description |
|---|---|---|
| `Station_Name` | String | Name of the charging hub facility |
| `Address` | String | Physical address of the charging station |
| `Latitude` | Double | Geospatial latitude coordinate |
| `Longitude` | Double | Geospatial longitude coordinate |
| `Start_Date_Time` | Timestamp | Timestamp when the vehicle plugged in |
| `End_Date_Time` | Timestamp | Timestamp when charging session ended |
| `Total_Duration_hh_mm_ss`| String | Total duration connected to port |
| `Charging_Time_hh_mm_ss` | String | Active duration energy was delivered |
| `Energy__kWh_` | Double | Total energy transferred in kilowatt-hours |
| `Port_Type` | String | Level 2 AC or DC Fast Charger |
| `Port_Number` | Integer | Specific bay identifier at the station |
| `User_ID` | String | Anonymized unique driver identifier |

---

## 3. End-to-End Distributed Big Data Pipeline

### 3.1 Data Ingestion & Streaming Layer
- **Live Stream Simulation:** A Python-based event generator simulates continuous EV plug-in, heartbeat telemetry, and plug-out events over Apache Kafka.
- **Spark Structured Streaming:** Subscribes to the Kafka event stream using tumbling and sliding 15-minute time windows:
  $$\text{Power Draw}(t) = \sum_{i \in \text{Active Sessions}} P_i(t)$$
- Computes real-time transformer utilization rates and triggers alerts when instantaneous load exceeds 85% of rated capacity.

### 3.2 Distributed Storage & Processing Layer
- **Data Lakehouse:** Cleaned and transformed sessions are partitioned by year/month and written in columnar **Apache Parquet** format for efficient analytical queries.
- **PySpark Feature Engineering:**
  - Temporal decomposition: `hour_of_day`, `day_of_week`, `is_weekend`, `season`.
  - Spatial feature vectors: `[latitude, longitude]`.
  - `VectorAssembler` and `StandardScaler` for distributed matrix pipelines.

### 3.3 PySpark MLlib Intelligence Engine (5 Models)

#### Model 1: Gradient Boosted Tree Regressor (`GBTRegressor`)
- **Objective:** Predict next-hour aggregate grid energy demand ($kWh$) per substation.
- **Features:** Lagged hourly load, rolling moving average, temperature/weather proxy, day-of-week, hour-of-day.
- **Evaluation:** Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), $R^2$.

#### Model 2: Random Forest Regressor (`RandomForestRegressor`)
- **Objective:** Benchmark comparative model against GBTRegressor for grid load prediction.
- **Hyperparameter Tuning:** `numTrees` (50, 100), `maxDepth` (5, 10) via `ParamGridBuilder` and `CrossValidator`.

#### Model 3: Random Forest Classifier (`RandomForestClassifier`)
- **Objective:** Classify station bay congestion level into discrete categories: `Low` (available slots), `Moderate`, `High` (queues expected).
- **Features:** Historical arrival frequency, active port ratio, time-of-day, proximity to commercial centers.
- **Evaluation:** Multi-class Accuracy, Precision, Recall, F1-Score, Multi-class ROC-AUC.

#### Model 4: Linear Regression (`LinearRegression`)
- **Objective:** Predict individual vehicle session charging duration (in minutes) upon plug-in.
- **Features:** Initial state-of-charge delta, port type (L2 vs DCFC), historical user average energy draw.
- **Evaluation:** RMSE, MAE, $R^2$.

#### Model 5: Spatial Clustering (`KMeans` & `BisectingKMeans`)
- **Objective:** Unsupervised spatial analysis to identify high-density charging demand centroids for installing new hubs.
- **Features:** Spatial coordinates `(Latitude, Longitude)` weighted by total energy consumption and session count.
- **Evaluation:** Silhouette Score with Euclidean distance, Within-Set Sum of Squared Errors (WSSSE).

---

## 4. Role-Based Multi-Persona Business Intelligence Dashboard

### Tab 1: Admin & Power Grid Operations Center
- **Real-Time Load Monitor:** Current active kW draw across all stations vs. substation transformer threshold.
- **Predictive 24-Hour Load Curve:** Actual vs. PySpark `GBTRegressor` predicted hourly consumption.
- **Port Breakdown:** Energy draw distribution (DC Fast Charging vs. Level 2 AC).
- **Peak Overload Alerts:** Real-time visual indicator flagging high-stress substations.

### Tab 2: Smart EV Driver Companion
- **Station Bay Availability:** Live status per charging station (Free / Occupied / Reserved).
- **Queue Congestion Gauge:** Real-time ML classification indicator (Low / Moderate / Congested).
- **Session Duration Estimator:** Interactive calculator estimating minutes remaining for plugged-in vehicles.
- **Filter Bar:** Filtering by Connector Type (CCS2, Type 2, CHAdeMO) and minimum charging power.

### Tab 3: Urban Planning & Infrastructure Siting Portal
- **Geographic Hotspot Map:** Heatmap of high-density charging usage across municipal zones.
- **Optimal Cluster Centroids:** Recommended geographic coordinates for next $K$ charging hubs calculated by PySpark `KMeans`.
- **Charging Desert Analysis:** Highlighted urban zones with high population density but zero fast chargers within a 5 km radius.
- **Siting Feasibility Matrix:** Ranking candidate sites by projected ROI and utilization index.

---

## 5. University Evaluation Milestones & Rubric Compliance

| Milestone | Window | Focus & Deliverables | Marks |
|---|---|---|---|
| **Milestone 1** | Oct 12–16 | Problem definition, literature review, project feasibility, objectives, methodology, algorithm selection. Minimum 20-page report (Chapters 1 & 2). | 6 Marks |
| **Milestone 2** | Oct 26–29 | Working PySpark implementation, 5 ML models, streaming telemetry demo, code viva voce, Chapter 3 & 4 report additions (pages 23–42). | 12 Marks |
| **Milestone 3** | Nov 16–20 | Final complete report (Chapters 1–5, 45–50 pages), full code repository, datasets, experimental screenshots, viva demonstration. | 12 Marks |

### Plagiarism & Academic Integrity Standards:
- **Turnitin Similarity Index:** $<10\%$ for full marks (100% mark retention).
- **AI Plagiarism:** Strictly $0\%$ AI similarity required by course guidelines.


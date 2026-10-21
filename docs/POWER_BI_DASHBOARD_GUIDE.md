# VoltPulse: Complete Power BI Business Intelligence Dashboard Implementation Guide

This guide details the exact structure, DAX formulas, visual configurations, and role-based tabs required to build and submit the **Power BI Dashboard** for the Big Data Project evaluation (satisfying **Clause 3e: Data Visualization and Business Intelligence** of the course rubric).

---

## 1. Why Power BI is Used in this Project
In enterprise Big Data architectures, there is a clear division between:
* **Apache Spark / PySpark:** High-performance distributed computation engine (cleans millions of raw telemetry logs and trains ML models).
* **Power BI:** The executive Business Intelligence (BI) layer used by decision-makers (grid managers, municipal authorities, network executives) for interactive drag-and-drop filtering, drill-downs, KPI tracking, and spatial mapping.
* **Streamlit (`src/dashboard/app.py`):** Acts as the live engineering prototype / web application showing model inference in real-time.

---

## 2. Power BI Data Source Connection
1. Open **Power BI Desktop**.
2. Click **Get Data** ➔ **Text/CSV**.
3. Select:
   ```
   d:\bennett\bigdata_project\data\processed\cleaned_sessions.csv
   ```
4. Click **Load** (or Transform Data to verify types):
   * `Start_Date_Time` ➔ Date/Time
   * `Latitude` ➔ Decimal Number (Data Category: *Latitude*)
   * `Longitude` ➔ Decimal Number (Data Category: *Longitude*)
   * `Energy_kWh` ➔ Decimal Number
   * `Total_Duration_Minutes` ➔ Decimal Number

---

## 3. Core DAX Measures (Copy & Paste into Power BI)

Click **Modeling** ➔ **New Measure** and add these formulas:

### Measure 1: Total Energy Delivered (MWh)
```dax
Total Energy (MWh) = SUM(cleaned_sessions[Energy_kWh]) / 1000
```

### Measure 2: Average Charging Duration (Minutes)
```dax
Avg Duration (Mins) = AVERAGE(cleaned_sessions[Charging_Duration_Minutes])
```

### Measure 3: Grid Peak Power Draw (kW)
```dax
Peak Power Draw (kW) = 
VAR TotalKWh = SUM(cleaned_sessions[Energy_kWh])
VAR TotalHours = SUM(cleaned_sessions[Charging_Duration_Minutes]) / 60
RETURN
DIVIDE(TotalKWh, TotalHours, 0)
```

### Measure 4: Substation Headroom Stress Index (%)
```dax
Grid Headroom Stress % = 
VAR RatedSubstationCapacity = 800 -- Rated kW capacity
VAR CurrentLoad = [Peak Power Draw (kW)]
RETURN
MIN(100, DIVIDE(CurrentLoad, RatedSubstationCapacity, 0) * 100)
```

### Measure 5: High-Congestion Ratio
```dax
High Congestion Session % = 
DIVIDE(
    CALCULATE(COUNTROWS(cleaned_sessions), cleaned_sessions[Congestion_Level] = 2),
    COUNTROWS(cleaned_sessions),
    0
) * 100
```

---

## 4. Multi-Page Dashboard Design (3 Role-Based Tabs)

Create 3 distinct canvas tabs in Power BI to mirror the project architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│  ⚡ VOLTPULSE: ENTERPRISE BIG DATA & BI PLATFORM                       │
├─────────────────────┬──────────────────────┬───────────────────────────┤
│ Tab 1: Grid Admin   │ Tab 2: Driver Portal │ Tab 3: Urban Site Planner │
└─────────────────────┴──────────────────────┴───────────────────────────┘
```

---

### Tab 1: Grid Operations & Substation Center (Admin View)
*Target Persona: Electricity Utility NOC & Grid Reliability Operators*

1. **Card KPIs (Top Row):**
   * Card 1: `[Total Energy (MWh)]`
   * Card 2: `[Peak Power Draw (kW)]`
   * Card 3: `Total Sessions` (`COUNTROWS(cleaned_sessions)`)
2. **Gauge Visual:**
   * Value: `[Grid Headroom Stress %]`
   * Target: `85%` (Safe threshold warning)
3. **Line and Clustered Column Chart (24-Hour Load Profile):**
   * Shared Axis: `Hour` (0 to 23)
   * Column Values: `[Total Energy Delivered]` (Actual hourly load)
   * Tooltip: `DayOfWeek`
4. **Donut Chart (Port Standard Distribution):**
   * Legend: `Port_Type` (DC Fast vs. Level 2)
   * Values: `[Total Energy Delivered]`
5. **Slicer Bar:**
   * Slicer 1: `IsWeekend` (Weekday vs. Weekend load comparison)
   * Slicer 2: `Station_Name`

---

### Tab 2: Smart EV Driver Companion (User View)
*Target Persona: EV Drivers navigating to charging hubs*

1. **Top Slicer / Search:**
   * Dropdown: `Station_Name`
2. **Multi-Row Card:**
   * Selected Facility Address: `Address`
   * Charger Standard: `Port_Type`
   * Available Bays: `Port_Number`
3. **Clustered Bar Chart (Hourly Wait & Congestion Profile):**
   * Y-Axis: `Hour`
   * X-Axis: `Count of Sessions`
   * Color saturation: `Congestion_Level` (Green = Low, Amber = Moderate, Red = Congested)
4. **Scatter Chart (Charging Time vs. Energy Delivered):**
   * X-Axis: `Energy_kWh`
   * Y-Axis: `Charging_Duration_Minutes`
   * Details: `User_ID`
   * Legend: `Port_Type`

---

### Tab 3: Urban Planning & Siting Analytics (City Planner View)
*Target Persona: Municipal Corporations & Commercial Real Estate Siting*

1. **Map Visual (Bubble Map):**
   * Latitude: `Latitude`
   * Longitude: `Longitude`
   * Size: `[Total Energy (MWh)]`
   * Color: `[High Congestion Session %]`
   * Tooltips: `Station_Name`, `Address`, `Total Sessions`
2. **Matrix Visual (Hub Performance & Expansion Priority):**
   * Rows: `Station_Name`
   * Columns: `Port_Type`
   * Values: `[Total Energy (MWh)]`, `[Avg Duration (Mins)]`, `Total Sessions`
3. **Decomposition Tree:**
   * Analyze: `Energy_kWh`
   * Explain by: `Station_Name` ➔ `Port_Type` ➔ `IsWeekend` ➔ `Hour`
   *(Demonstrates root-cause analytics of energy demand drivers for viva evaluations).*

---

## 5. What to Include in the University Project Report & Viva

For **Milestone 2** and **Milestone 3** evaluation:
1. **Screenshots:** Take 3 high-resolution screenshots of the 3 Power BI pages and insert them into **Chapter 4 (Results & Business Intelligence)** of the report.
2. **Viva Talking Points:**
   * *"PySpark MLlib handles the heavy distributed computation, streaming aggregation, and model training in the backend."*
   * *"Power BI acts as the executive decision-support layer, consuming the transformed Parquet/CSV data and providing interactive DAX-powered KPIs for utility admins and city planners."*
   * *"The 3-tab layout satisfies the multi-persona enterprise requirements, solving grid overload, driver waiting times, and urban charging desert placement."*


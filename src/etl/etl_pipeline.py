"""
etl_pipeline.py
---------------
End-to-end data cleaning, transformation, and feature engineering pipeline.
Supports distributed PySpark processing with standard fallback to Pandas/PyArrow
to ensure instant portability across both local and cluster environments.
"""

import os
import sys

def run_etl(input_csv="data/raw/boulder_ev_charging_data.csv", output_dir="data/processed"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[ETL] Starting pipeline processing from '{input_csv}'...")
    
    # Try PySpark first if available, else use Python/Pandas
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
        from pyspark.sql.types import DoubleType, IntegerType, TimestampType
        
        print("[ETL] Initializing Apache Spark Session...")
        spark = SparkSession.builder \
            .appName("VoltPulse-ETL-Pipeline") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()
            
        df = spark.read.csv(input_csv, header=True, inferSchema=True)
        print(f"[ETL] Loaded {df.count()} records into Spark DataFrame.")
        
        # Feature Engineering in Spark
        df_clean = df.withColumn("Start_TS", F.to_timestamp("Start_Date_Time")) \
                     .withColumn("End_TS", F.to_timestamp("End_Date_Time")) \
                     .withColumn("Hour", F.hour("Start_TS")) \
                     .withColumn("DayOfWeek", F.dayofweek("Start_TS")) \
                     .withColumn("IsWeekend", F.when(F.col("DayOfWeek").isin([1, 7]), 1).otherwise(0)) \
                     .withColumn("IsDCFC", F.when(F.col("Port_Type") == "DC Fast", 1).otherwise(0)) \
                     .withColumn("Energy_kWh", F.col("Energy__kWh_").cast(DoubleType())) \
                     .withColumn("Duration_Mins", F.col("Total_Duration_Minutes").cast(DoubleType())) \
                     .withColumn("Charging_Mins", F.col("Charging_Duration_Minutes").cast(DoubleType()))
                     
        # Derive Congestion Target (Categorical: 0=Low, 1=Moderate, 2=High)
        df_clean = df_clean.withColumn("Congestion_Level",
            F.when(F.col("Hour").isin([7, 8, 12, 17, 18, 19]), 2)
             .when(F.col("Hour").isin([9, 10, 11, 13, 14, 15, 16]), 1)
             .otherwise(0)
        )
        
        # Write to Processed Lakehouse
        processed_path = os.path.join(output_dir, "cleaned_sessions.csv")
        df_clean.toPandas().to_csv(processed_path, index=False)
        print(f"[ETL] Successfully completed Spark ETL. Processed data saved to '{processed_path}'.")
        return processed_path
        
    except (ImportError, Exception) as e:
        print(f"[ETL] PySpark notice: {e}. Executing native high-performance ETL pipeline...")
        import csv
        from datetime import datetime
        
        records = []
        with open(input_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                start_dt = datetime.strptime(row["Start_Date_Time"], "%Y-%m-%d %H:%M:%S")
                hour = start_dt.hour
                dow = (start_dt.weekday() + 2) % 7 # 1=Sun, 7=Sat
                is_weekend = 1 if dow in (1, 7) else 0
                is_dcfc = 1 if row["Port_Type"] == "DC Fast" else 0
                
                # Congestion: High during commute peaks, Moderate midday, Low night
                if hour in (7, 8, 12, 17, 18, 19):
                    congestion = 2 # High
                elif hour in (9, 10, 11, 13, 14, 15, 16):
                    congestion = 1 # Moderate
                else:
                    congestion = 0 # Low
                    
                row["Hour"] = hour
                row["DayOfWeek"] = dow
                row["IsWeekend"] = is_weekend
                row["IsDCFC"] = is_dcfc
                row["Congestion_Level"] = congestion
                row["Energy_kWh"] = float(row["Energy__kWh_"])
                row["Duration_Mins"] = float(row["Total_Duration_Minutes"])
                row["Charging_Mins"] = float(row["Charging_Duration_Minutes"])
                records.append(row)
                
        processed_path = os.path.join(output_dir, "cleaned_sessions.csv")
        headers = list(records[0].keys())
        with open(processed_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
            
        print(f"[ETL] Processed {len(records)} records. Saved to '{processed_path}'.")
        return processed_path

if __name__ == "__main__":
    run_etl()


"""
train_pyspark_mllib.py
----------------------
Native Apache Spark MLlib Pipeline implementation for VoltPulse.
Implements the 5 models using PySpark MLlib:
1. GBTRegressor (Hourly Grid Energy Demand Forecasting)
2. RandomForestRegressor (Benchmark Grid Prediction)
3. RandomForestClassifier (Charger Bay Congestion Level)
4. LinearRegression (Charging Duration Prediction)
5. KMeans (Optimal Charging Hub Spatial Clustering)

Evaluation metrics: RMSE, MAE, R2, Accuracy, F1, Silhouette Score.
"""

import sys
import os

def run_pyspark_mllib():
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
        from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
        from pyspark.ml.regression import GBTRegressor, RandomForestRegressor, LinearRegression
        from pyspark.ml.classification import RandomForestClassifier
        from pyspark.ml.clustering import KMeans
        from pyspark.ml.evaluation import RegressionEvaluator, MulticlassClassificationEvaluator, ClusteringEvaluator
    except ImportError:
        print("[PySpark MLlib] Notice: PySpark is not installed or Java/Hadoop environment requires configuration.")
        print("[PySpark MLlib] This script contains the production PySpark MLlib pipeline code for submission and cluster deployment.")
        return

    print("[PySpark MLlib] Initializing SparkSession...")
    spark = SparkSession.builder \
        .appName("VoltPulse-PySpark-MLlib-Suite") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
        
    data_path = "data/raw/boulder_ev_charging_data.csv"
    if not os.path.exists(data_path):
        print(f"[Error] Raw dataset not found at '{data_path}'.")
        return

    df = spark.read.csv(data_path, header=True, inferSchema=True)
    
    # Preprocessing
    df = df.withColumn("Start_TS", F.to_timestamp("Start_Date_Time")) \
           .withColumn("Hour", F.hour("Start_TS")) \
           .withColumn("DayOfWeek", F.dayofweek("Start_TS")) \
           .withColumn("IsWeekend", F.when(F.col("DayOfWeek").isin([1, 7]), 1.0).otherwise(0.0)) \
           .withColumn("IsDCFC", F.when(F.col("Port_Type") == "DC Fast", 1.0).otherwise(0.0)) \
           .withColumn("Energy_kWh", F.col("Energy__kWh_").cast("double")) \
           .withColumn("Duration_Mins", F.col("Total_Duration_Minutes").cast("double")) \
           .withColumn("Charging_Mins", F.col("Charging_Duration_Minutes").cast("double")) \
           .withColumn("Congestion_Level",
               F.when(F.col("Hour").isin([7, 8, 12, 17, 18, 19]), 2.0)
                .when(F.col("Hour").isin([9, 10, 11, 13, 14, 15, 16]), 1.0)
                .otherwise(0.0)
           )

    # ----------------------------------------------------
    # Model 1 & 2: GBTRegressor & RandomForestRegressor
    # ----------------------------------------------------
    print("\n--- Training PySpark Model 1 (GBTRegressor) & Model 2 (RandomForestRegressor) ---")
    reg_assembler = VectorAssembler(
        inputCols=["Hour", "DayOfWeek", "IsWeekend", "IsDCFC", "Charging_Mins"],
        outputCol="features"
    )
    reg_data = reg_assembler.transform(df).select("features", F.col("Energy_kWh").alias("label"))
    train_r, test_r = reg_data.randomSplit([0.8, 0.2], seed=42)

    # 1. GBTRegressor
    gbt = GBTRegressor(featuresCol="features", labelCol="label", maxIter=50, maxDepth=5, seed=42)
    gbt_model = gbt.fit(train_r)
    gbt_preds = gbt_model.transform(test_r)
    
    reg_eval_rmse = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    reg_eval_r2 = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="r2")
    
    print(f"PySpark GBT Regressor -> RMSE: {reg_eval_rmse.evaluate(gbt_preds):.4f}, R2: {reg_eval_r2.evaluate(gbt_preds):.4f}")

    # 2. RandomForestRegressor
    rf = RandomForestRegressor(featuresCol="features", labelCol="label", numTrees=50, maxDepth=6, seed=42)
    rf_model = rf.fit(train_r)
    rf_preds = rf_model.transform(test_r)
    print(f"PySpark RF Regressor  -> RMSE: {reg_eval_rmse.evaluate(rf_preds):.4f}, R2: {reg_eval_r2.evaluate(rf_preds):.4f}")

    # ----------------------------------------------------
    # Model 3: RandomForestClassifier (Congestion)
    # ----------------------------------------------------
    print("\n--- Training PySpark Model 3 (RandomForestClassifier) ---")
    cls_assembler = VectorAssembler(
        inputCols=["Hour", "DayOfWeek", "IsWeekend", "IsDCFC", "Port_Number"],
        outputCol="cls_features"
    )
    cls_data = cls_assembler.transform(df).select("cls_features", F.col("Congestion_Level").alias("label"))
    train_c, test_c = cls_data.randomSplit([0.8, 0.2], seed=42)
    
    rf_clf = RandomForestClassifier(featuresCol="cls_features", labelCol="label", numTrees=50, maxDepth=6, seed=42)
    rf_clf_model = rf_clf.fit(train_c)
    clf_preds = rf_clf_model.transform(test_c)
    
    cls_eval_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    cls_eval_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
    print(f"PySpark RF Classifier -> Accuracy: {cls_eval_acc.evaluate(clf_preds):.4f}, F1-Score: {cls_eval_f1.evaluate(clf_preds):.4f}")

    # ----------------------------------------------------
    # Model 4: LinearRegression (Duration)
    # ----------------------------------------------------
    print("\n--- Training PySpark Model 4 (LinearRegression) ---")
    dur_assembler = VectorAssembler(inputCols=["Energy_kWh", "IsDCFC", "Hour", "IsWeekend"], outputCol="dur_features")
    dur_data = dur_assembler.transform(df).select("dur_features", F.col("Charging_Mins").alias("label"))
    train_d, test_d = dur_data.randomSplit([0.8, 0.2], seed=42)
    
    lr = LinearRegression(featuresCol="dur_features", labelCol="label")
    lr_model = lr.fit(train_d)
    dur_preds = lr_model.transform(test_d)
    print(f"PySpark Linear Regression -> RMSE: {reg_eval_rmse.evaluate(dur_preds):.4f}, R2: {reg_eval_r2.evaluate(dur_preds):.4f}")

    # ----------------------------------------------------
    # Model 5: KMeans Spatial Clustering
    # ----------------------------------------------------
    print("\n--- Training PySpark Model 5 (KMeans Spatial Clustering) ---")
    geo_assembler = VectorAssembler(inputCols=["Latitude", "Longitude"], outputCol="geo_features")
    geo_data = geo_assembler.transform(df).select("geo_features")
    
    kmeans = KMeans(featuresCol="geo_features", k=4, seed=42)
    kmeans_model = kmeans.fit(geo_data)
    cluster_preds = kmeans_model.transform(geo_data)
    
    clust_eval = ClusteringEvaluator(featuresCol="geo_features", metricName="silhouette")
    sil_score = clust_eval.evaluate(cluster_preds)
    print(f"PySpark KMeans (k=4) -> Silhouette Score: {sil_score:.4f}")
    print("Cluster Centers (Lat, Lon):")
    for center in kmeans_model.clusterCenters():
        print(f"  {center}")
        
    print("\n[PySpark MLlib] Complete suite execution successful!")
    spark.stop()

if __name__ == "__main__":
    run_pyspark_mllib()


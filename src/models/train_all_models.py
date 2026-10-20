"""
train_all_models.py
-------------------
Trains and evaluates all 5 ML models required by the curriculum rubric:
1. Admin Portal: GBT Regressor (Next-hour Grid Power Load Forecast)
2. Admin Portal: Random Forest Regressor (Benchmark comparison)
3. Driver Portal: Random Forest Classifier (Station Bay Congestion Level)
4. Driver Portal: Linear Regression (Session Duration Prediction)
5. City Planner Portal: K-Means Spatial Clustering (Optimal Hub Siting)

Computes full evaluation metrics:
- Regression: RMSE, MAE, R^2
- Classification: Accuracy, Precision, Recall, F1-Score
- Clustering: Silhouette Score, Inertia (WSSSE)
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, silhouette_score

def train_and_evaluate(input_csv="data/processed/cleaned_sessions.csv", output_metrics_path="data/processed/model_metrics.json"):
    print("[ML Engine] Loading processed sessions dataset...")
    df = pd.read_csv(input_csv)
    print(f"[ML Engine] Dataset contains {len(df)} records.")
    
    metrics_summary = {}

    # ----------------------------------------------------
    # Module 1 & 2: Admin Portal Grid Load Forecasting (GBT vs RF)
    # ----------------------------------------------------
    print("\n--- Training Model 1 (GBT Regressor) & Model 2 (RF Regressor) ---")
    # Feature matrix for energy prediction
    X_reg = df[["Hour", "DayOfWeek", "IsWeekend", "IsDCFC", "Charging_Duration_Minutes"]]
    y_reg = df["Energy_kWh"]
    
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
    
    # 1. GBT Regressor
    gbt = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
    gbt.fit(X_train_r, y_train_r)
    gbt_pred = gbt.predict(X_test_r)
    
    gbt_metrics = {
        "model_name": "Gradient Boosted Tree Regressor (GBT)",
        "module": "Admin / Grid Load Forecasting",
        "RMSE": round(float(np.sqrt(mean_squared_error(y_test_r, gbt_pred))), 4),
        "MAE": round(float(mean_absolute_error(y_test_r, gbt_pred)), 4),
        "R2_Score": round(float(r2_score(y_test_r, gbt_pred)), 4)
    }
    metrics_summary["Model_1_GBT_Regressor"] = gbt_metrics
    print(f"GBT Regressor -> RMSE: {gbt_metrics['RMSE']}, MAE: {gbt_metrics['MAE']}, R2: {gbt_metrics['R2_Score']}")

    # 2. Random Forest Regressor (Benchmark)
    rf_reg = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    rf_reg.fit(X_train_r, y_train_r)
    rf_pred = rf_reg.predict(X_test_r)
    
    rf_reg_metrics = {
        "model_name": "Random Forest Regressor",
        "module": "Admin / Grid Load Benchmark",
        "RMSE": round(float(np.sqrt(mean_squared_error(y_test_r, rf_pred))), 4),
        "MAE": round(float(mean_absolute_error(y_test_r, rf_pred)), 4),
        "R2_Score": round(float(r2_score(y_test_r, rf_pred)), 4)
    }
    metrics_summary["Model_2_RF_Regressor"] = rf_reg_metrics
    print(f"RF Regressor  -> RMSE: {rf_reg_metrics['RMSE']}, MAE: {rf_reg_metrics['MAE']}, R2: {rf_reg_metrics['R2_Score']}")

    # ----------------------------------------------------
    # Module 3: Driver Portal Congestion Classification
    # ----------------------------------------------------
    print("\n--- Training Model 3 (Random Forest Classifier) ---")
    X_cls = df[["Hour", "DayOfWeek", "IsWeekend", "IsDCFC", "Port_Number"]]
    y_cls = df["Congestion_Level"]
    
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_cls, y_cls, test_size=0.2, random_state=42)
    
    rf_clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf_clf.fit(X_train_c, y_train_c)
    clf_pred = rf_clf.predict(X_test_c)
    
    clf_metrics = {
        "model_name": "Random Forest Classifier",
        "module": "Driver / Station Congestion Level",
        "Accuracy": round(float(accuracy_score(y_test_c, clf_pred)), 4),
        "Precision": round(float(precision_score(y_test_c, clf_pred, average="weighted", zero_division=0)), 4),
        "Recall": round(float(recall_score(y_test_c, clf_pred, average="weighted", zero_division=0)), 4),
        "F1_Score": round(float(f1_score(y_test_c, clf_pred, average="weighted", zero_division=0)), 4)
    }
    metrics_summary["Model_3_RF_Classifier"] = clf_metrics
    print(f"RF Classifier -> Accuracy: {clf_metrics['Accuracy']}, F1: {clf_metrics['F1_Score']}, Precision: {clf_metrics['Precision']}")

    # ----------------------------------------------------
    # Module 4: Driver Portal Session Duration Estimation
    # ----------------------------------------------------
    print("\n--- Training Model 4 (Linear Regression Duration Model) ---")
    X_dur = df[["Energy_kWh", "IsDCFC", "Hour", "IsWeekend"]]
    y_dur = df["Charging_Duration_Minutes"]
    
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_dur, y_dur, test_size=0.2, random_state=42)
    
    lr = LinearRegression()
    lr.fit(X_train_d, y_train_d)
    dur_pred = lr.predict(X_test_d)
    
    dur_metrics = {
        "model_name": "Linear Regression",
        "module": "Driver / Session Duration Prediction",
        "RMSE": round(float(np.sqrt(mean_squared_error(y_test_d, dur_pred))), 4),
        "MAE": round(float(mean_absolute_error(y_test_d, dur_pred)), 4),
        "R2_Score": round(float(r2_score(y_test_d, dur_pred)), 4)
    }
    metrics_summary["Model_4_Linear_Regression"] = dur_metrics
    print(f"Linear Regression -> RMSE: {dur_metrics['RMSE']} mins, MAE: {dur_metrics['MAE']} mins, R2: {dur_metrics['R2_Score']}")

    # ----------------------------------------------------
    # Module 5: City Planner Spatial Clustering
    # ----------------------------------------------------
    print("\n--- Training Model 5 (K-Means Spatial Clustering) ---")
    coords = df[["Latitude", "Longitude"]].drop_duplicates()
    
    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(coords)
    sil_score = silhouette_score(coords, cluster_labels)
    
    centroids = kmeans.cluster_centers_.tolist()
    kmeans_metrics = {
        "model_name": "K-Means Spatial Clustering",
        "module": "City Planner / Hub Siting Optimization",
        "K_Clusters": k,
        "Silhouette_Score": round(float(sil_score), 4),
        "WSSSE_Inertia": round(float(kmeans.inertia_), 4),
        "Recommended_Centroids_Lat_Lon": centroids
    }
    metrics_summary["Model_5_KMeans_Clustering"] = kmeans_metrics
    print(f"K-Means (k={k}) -> Silhouette Score: {kmeans_metrics['Silhouette_Score']}, WSSSE: {kmeans_metrics['WSSSE_Inertia']}")
    print(f"Recommended Centroids:\n{centroids}")

    # Save summary
    with open(output_metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=4)
        
    print(f"\n[ML Engine] All 5 models trained and evaluated successfully!")
    print(f"[ML Engine] Comparative metrics saved to '{output_metrics_path}'.")
    return metrics_summary

if __name__ == "__main__":
    train_and_evaluate()


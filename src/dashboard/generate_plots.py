"""
generate_plots.py
-----------------
Generates publication-quality evaluation charts and plots for the report and PPT:
1. Session energy grouped by start hour
2. Held-out regression benchmark comparison
3. Sample station coordinates and benchmark centroids
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_charts(output_dir="data/processed/plots"):
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # 1. Hourly Load Curve
    csv_path = "data/processed/cleaned_sessions.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        hourly = df.groupby("Hour")["Energy_kWh"].sum().reindex(range(24), fill_value=0)
        
        plt.figure(figsize=(10, 5))
        plt.bar(hourly.index, hourly, color="#067467")
        plt.title("Energy delivered by session start hour", fontsize=13, fontweight="bold")
        plt.xlabel("Session start hour", fontsize=11)
        plt.ylabel("Total session energy (kWh)", fontsize=11)
        plt.xticks(range(24))
        plt.tight_layout()
        plot1 = os.path.join(output_dir, "hourly_load_profile.png")
        plt.savefig(plot1, dpi=300)
        plt.close()
        print(f"[Plots] Saved: {plot1}")
        
    # 2. Model Performance Comparison Bar Chart
    metrics_path = "data/processed/model_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            m = json.load(f)
            
        models = ["GBT Regressor", "RF Regressor"]
        rmse_vals = [m["Model_1_GBT_Regressor"]["RMSE"], m["Model_2_RF_Regressor"]["RMSE"]]
        fig, axis = plt.subplots(figsize=(8, 4.5))
        bars = axis.barh(models, rmse_vals, color=["#39759a", "#067467"])
        axis.invert_yaxis()
        axis.set_xlim(0, max(rmse_vals) * 1.2)
        axis.bar_label(bars, fmt="%.4f", padding=5)
        axis.set_xlabel("RMSE (kWh)")
        axis.set_title("Session energy prediction error (scikit-learn benchmark)", fontsize=12, fontweight="bold")
        fig.tight_layout()
        plot2 = os.path.join(output_dir, "model_comparison_bar.png")
        plt.savefig(plot2, dpi=300)
        plt.close()
        print(f"[Plots] Saved: {plot2}")

    # 3. Spatial Siting Centroids Plot
    if os.path.exists(csv_path) and os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            m = json.load(f)
        centroids = np.array(m["Model_5_KMeans_Clustering"]["Recommended_Centroids_Lat_Lon"])
        
        plt.figure(figsize=(8, 6))
        coords = df[["Latitude", "Longitude"]].drop_duplicates()
        plt.scatter(coords["Longitude"], coords["Latitude"], c="#39759a", s=30, label="Sample station location")
        plt.scatter(centroids[:, 1], centroids[:, 0], c="#db6a26", marker="s", s=100, label="Benchmark centroid")
        plt.title("Station coordinates and K-means centroids", fontsize=13, fontweight="bold")
        plt.xlabel("Longitude", fontsize=11)
        plt.ylabel("Latitude", fontsize=11)
        plt.legend(frameon=True)
        plt.tight_layout()
        plot3 = os.path.join(output_dir, "spatial_hub_centroids.png")
        plt.savefig(plot3, dpi=300)
        plt.close()
        print(f"[Plots] Saved: {plot3}")

if __name__ == "__main__":
    generate_charts()


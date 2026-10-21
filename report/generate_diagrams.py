"""
generate_diagrams.py
--------------------
Produces publication-quality architectural and methodology diagrams
for the VoltPulse Milestone 1 report.  Every diagram is saved as a
standalone PNG image inside  report/diagrams/ .
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(OUT, exist_ok=True)

# ── colour palette ──
C_BLUE   = "#2c5f8a"
C_TEAL   = "#1a8a7d"
C_ORANGE = "#d17a22"
C_RED    = "#b5403a"
C_GREEN  = "#3a8a47"
C_PURPLE = "#6b3fa0"
C_GRAY   = "#555555"
C_LIGHT  = "#f0f4f8"


# ====================================================================
#  1.  Four-Layer System Architecture Diagram
# ====================================================================
def draw_system_architecture():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    layers = [
        (0.5, 6.0, 9.0, 1.4, C_BLUE,
         "Layer 1 — Data Ingestion & Streaming",
         ["City of Boulder Open Data\n(Authentic CSV Logs)",
          "Apache Kafka\nEvent Producer",
          "Live JSONL\nTelemetry Stream"]),
        (0.5, 4.2, 9.0, 1.4, C_TEAL,
         "Layer 2 — Distributed Spark Processing",
         ["PySpark Batch\nETL Pipeline",
          "Spark Structured\nStreaming Engine",
          "Apache Parquet\nLakehouse Storage"]),
        (0.5, 2.4, 9.0, 1.4, C_ORANGE,
         "Layer 3 — PySpark MLlib Intelligence",
         ["GBT / RF\nRegressors",
          "RF Classifier\n(Congestion)",
          "K-Means\nSpatial Clustering"]),
        (0.5, 0.6, 9.0, 1.4, C_PURPLE,
         "Layer 4 — Role-Based BI Dashboard",
         ["Admin Grid\nOperations Console",
          "EV Driver\nCompanion Portal",
          "City Planner\nSiting Portal"]),
    ]

    for (x, y, w, h, colour, title, boxes) in layers:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                              facecolor=colour, alpha=0.18,
                              edgecolor=colour, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x + 0.15, y + h - 0.22, title,
                fontsize=9.5, fontweight="bold", color=colour, va="top")

        bw = 2.4
        gap = (w - 3 * bw) / 4
        for i, label in enumerate(boxes):
            bx = x + gap + i * (bw + gap)
            by = y + 0.15
            inner = FancyBboxPatch((bx, by), bw, 0.8,
                                   boxstyle="round,pad=0.06",
                                   facecolor="white", edgecolor=colour,
                                   linewidth=1.2)
            ax.add_patch(inner)
            ax.text(bx + bw / 2, by + 0.4, label,
                    fontsize=7.5, ha="center", va="center", color=C_GRAY)

    # arrows between layers
    for y_start, y_end in [(6.0, 5.6), (4.2, 3.8), (2.4, 2.0)]:
        ax.annotate("", xy=(5, y_start - 1.4 + 0.05), xytext=(5, y_start - 0.05),
                    arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=1.6))

    ax.set_title("VoltPulse — Four-Layer System Architecture",
                 fontsize=13, fontweight="bold", pad=14, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "system_architecture.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] system_architecture.png saved.")


# ====================================================================
#  2.  CRISP-DM Methodology Workflow (circular)
# ====================================================================
def draw_crisp_dm():
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    phases = [
        ("Domain\nModelling", C_BLUE),
        ("Data\nAcquisition", C_TEAL),
        ("Feature\nEngineering", C_GREEN),
        ("Model\nTraining", C_ORANGE),
        ("Evaluation &\nTuning", C_RED),
        ("BI Dashboard\nDeployment", C_PURPLE),
    ]
    n = len(phases)
    R = 1.1
    angles = [np.pi / 2 - 2 * np.pi * i / n for i in range(n)]

    for i, ((label, colour), ang) in enumerate(zip(phases, angles)):
        cx, cy = R * np.cos(ang), R * np.sin(ang)
        circle = plt.Circle((cx, cy), 0.35, facecolor=colour,
                             alpha=0.22, edgecolor=colour, linewidth=2)
        ax.add_patch(circle)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=colour)

        # arrow to next
        ang2 = angles[(i + 1) % n]
        nx, ny = R * np.cos(ang2), R * np.sin(ang2)
        dx, dy = nx - cx, ny - cy
        dist = np.sqrt(dx ** 2 + dy ** 2)
        ux, uy = dx / dist, dy / dist
        ax.annotate("", xy=(cx + ux * 0.42, cy + uy * 0.42),
                    xytext=(nx - ux * 0.42, ny - uy * 0.42),
                    arrowprops=dict(arrowstyle="<|-", color=C_GRAY,
                                   lw=1.3, connectionstyle="arc3,rad=0.15"))

    ax.text(0, 0, "CRISP-DM\nAdapted for\nBig Data", ha="center",
            va="center", fontsize=10, fontweight="bold", color=C_GRAY)
    ax.set_title("Adapted CRISP-DM Methodology Lifecycle",
                 fontsize=13, fontweight="bold", pad=14, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "crisp_dm_workflow.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] crisp_dm_workflow.png saved.")


# ====================================================================
#  3.  Data Flow Diagram (DFD Level 1)
# ====================================================================
def draw_dfd():
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    steps = [
        ("Raw Data\nSources", C_BLUE, 0.8),
        ("PySpark\nETL Cleaning", C_TEAL, 2.8),
        ("Feature\nVector\nAssembly", C_GREEN, 4.8),
        ("MLlib Model\nSuite\n(5 Models)", C_ORANGE, 6.8),
        ("Parquet\nLakehouse\nStorage", C_RED, 8.8),
        ("Power BI &\nStreamlit\nDashboard", C_PURPLE, 10.2),
    ]

    for label, colour, cx in steps:
        rect = FancyBboxPatch((cx - 0.7, 1.2), 1.4, 1.6,
                              boxstyle="round,pad=0.1",
                              facecolor=colour, alpha=0.15,
                              edgecolor=colour, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(cx, 2.0, label, ha="center", va="center",
                fontsize=8, fontweight="bold", color=colour)

    # arrows
    arrow_x = [(1.5, 2.1), (3.5, 4.1), (5.5, 6.1), (7.5, 8.1), (9.5, 9.5)]
    for (x1, x2) in arrow_x:
        ax.annotate("", xy=(x2, 2.0), xytext=(x1, 2.0),
                    arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=1.5))

    ax.set_title("VoltPulse — Data Flow Diagram (DFD Level 1)",
                 fontsize=12, fontweight="bold", pad=10, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dfd_level1.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] dfd_level1.png saved.")


# ====================================================================
#  4.  ETL Pipeline Flowchart
# ====================================================================
def draw_etl_flowchart():
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    steps = [
        (4.5, 6.8, "Boulder CSV\n(5000 sessions)", C_BLUE),
        (4.5, 5.8, "Read CSV into\nSpark DataFrame", C_TEAL),
        (4.5, 4.8, "Timestamp Parsing\n& Null Handling", C_GREEN),
        (4.5, 3.8, "Feature Engineering\n(Hour, DoW, IsWeekend, IsDCFC)", C_ORANGE),
        (4.5, 2.8, "Congestion Target\nDerivation (0 / 1 / 2)", C_RED),
        (4.5, 1.8, "StandardScaler &\nVectorAssembler", C_PURPLE),
        (4.5, 0.8, "Write Cleaned CSV &\nParquet Partitions", C_BLUE),
    ]

    for (cx, cy, label, colour) in steps:
        rect = FancyBboxPatch((cx - 1.8, cy - 0.35), 3.6, 0.7,
                              boxstyle="round,pad=0.08",
                              facecolor=colour, alpha=0.14,
                              edgecolor=colour, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=colour)

    for i in range(len(steps) - 1):
        y1 = steps[i][1] - 0.35
        y2 = steps[i + 1][1] + 0.35
        ax.annotate("", xy=(4.5, y2), xytext=(4.5, y1),
                    arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=1.4))

    ax.set_title("ETL Pipeline — Step-by-Step Processing Flowchart",
                 fontsize=12, fontweight="bold", pad=10, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "etl_flowchart.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] etl_flowchart.png saved.")


# ====================================================================
#  5.  ML Model Comparison Summary (bar chart)
# ====================================================================
def draw_model_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.patch.set_facecolor("white")

    # ---- Regression R² ----
    models_r = ["GBT Regressor", "RF Regressor", "Linear Reg\n(Duration)"]
    r2 = [0.7203, 0.7220, 0.8282]
    colours_r = [C_BLUE, C_TEAL, C_ORANGE]
    axes[0].barh(models_r, r2, color=colours_r, edgecolor="white", height=0.5)
    axes[0].set_xlim(0, 1.0)
    axes[0].set_xlabel("R² Score", fontsize=9)
    axes[0].set_title("Regression Model R² Comparison", fontsize=10, fontweight="bold")
    for i, v in enumerate(r2):
        axes[0].text(v + 0.02, i, f"{v:.4f}", va="center", fontsize=8.5)

    # ---- Classification ----
    metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
    vals = [0.95, 0.9577, 0.95, 0.9491]
    axes[1].bar(metrics, vals, color=[C_GREEN, C_PURPLE, C_RED, C_ORANGE],
                edgecolor="white", width=0.55)
    axes[1].set_ylim(0.9, 1.0)
    axes[1].set_ylabel("Score", fontsize=9)
    axes[1].set_title("RF Classifier — Congestion Metrics", fontsize=10, fontweight="bold")
    for i, v in enumerate(vals):
        axes[1].text(i, v + 0.002, f"{v:.4f}", ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "model_comparison.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] model_comparison.png saved.")


# ====================================================================
#  6.  Streaming Pipeline Schematic
# ====================================================================
def draw_streaming_pipeline():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    boxes = [
        (1.0, 1.5, "EV Vehicles\nPlug-in Events", C_BLUE),
        (3.2, 1.5, "Kafka\nProducer", C_TEAL),
        (5.4, 1.5, "Spark Structured\nStreaming\n(15-min Window)", C_ORANGE),
        (7.6, 1.5, "Overload\nAlert Engine\n(≥ 85% Cap)", C_RED),
        (9.2, 1.5, "Admin\nDashboard", C_PURPLE),
    ]

    for cx, cy, label, colour in boxes:
        rect = FancyBboxPatch((cx - 0.8, cy - 0.55), 1.6, 1.1,
                              boxstyle="round,pad=0.08",
                              facecolor=colour, alpha=0.16,
                              edgecolor=colour, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color=colour)

    pairs = [(1.8, 2.4), (4.0, 4.6), (6.2, 6.8), (8.4, 8.4)]
    for x1, x2 in pairs:
        ax.annotate("", xy=(x2, 1.5), xytext=(x1, 1.5),
                    arrowprops=dict(arrowstyle="-|>", color=C_GRAY, lw=1.3))

    ax.set_title("Real-Time Streaming Telemetry Pipeline",
                 fontsize=11, fontweight="bold", pad=8, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "streaming_pipeline.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] streaming_pipeline.png saved.")


# ====================================================================
#  7.  Dataset Schema Table as Image
# ====================================================================
def draw_dataset_schema():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    cols = ["Attribute", "Data Type", "Description"]
    rows = [
        ["Station_Name", "String", "Name of charging hub facility"],
        ["Address", "String", "Physical street address"],
        ["Latitude", "Double", "Geospatial latitude coordinate"],
        ["Longitude", "Double", "Geospatial longitude coordinate"],
        ["Start_Date_Time", "Timestamp", "Vehicle plug-in timestamp"],
        ["End_Date_Time", "Timestamp", "Session termination timestamp"],
        ["Total_Duration_Minutes", "Double", "Total connected duration (min)"],
        ["Charging_Duration_Minutes", "Double", "Active charging duration (min)"],
        ["Energy_kWh", "Double", "Energy transferred (kWh)"],
        ["Port_Type", "String", "Level 2 AC / DC Fast Charger"],
        ["Port_Number", "Integer", "Specific bay ID at station"],
        ["User_ID", "String", "Anonymised driver identifier"],
    ]

    table = ax.table(cellText=rows, colLabels=cols, loc="center",
                     cellLoc="left", colColours=[C_BLUE] * 3)
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1.0, 1.35)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(fontweight="bold", color="white")
            cell.set_facecolor(C_BLUE)
        else:
            cell.set_facecolor("#f7f9fb" if r % 2 == 0 else "white")
        cell.set_edgecolor("#cccccc")

    ax.set_title("City of Boulder EV Charging — Dataset Schema",
                 fontsize=11, fontweight="bold", pad=12, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dataset_schema.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] dataset_schema.png saved.")


# ====================================================================
#  8.  Tools & Technologies Stack Diagram
# ====================================================================
def draw_tech_stack():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    categories = [
        (1.5, 4.5, "Distributed\nCompute", "Apache Spark 3.5\nPySpark", C_BLUE),
        (4.5, 4.5, "Streaming", "Apache Kafka\nSpark Structured\nStreaming", C_TEAL),
        (7.5, 4.5, "Machine\nLearning", "PySpark MLlib\nScikit-learn", C_ORANGE),
        (1.5, 2.5, "Storage", "Apache Parquet\nCSV / JSONL", C_GREEN),
        (4.5, 2.5, "Visualization\n& BI", "Power BI Desktop\nStreamlit + Plotly", C_PURPLE),
        (7.5, 2.5, "Language\n& Runtime", "Python 3.14\nJupyter Notebooks", C_RED),
    ]

    for cx, cy, cat, tools, colour in categories:
        rect = FancyBboxPatch((cx - 1.2, cy - 0.7), 2.4, 1.4,
                              boxstyle="round,pad=0.1",
                              facecolor=colour, alpha=0.13,
                              edgecolor=colour, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(cx, cy + 0.35, cat, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=colour)
        ax.text(cx, cy - 0.2, tools, ha="center", va="center",
                fontsize=7.5, color=C_GRAY)

    ax.set_title("VoltPulse — Technology Stack Overview",
                 fontsize=12, fontweight="bold", pad=10, color=C_BLUE)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "tech_stack.png"), dpi=200)
    plt.close(fig)
    print("[Diagrams] tech_stack.png saved.")


# ====================================================================
if __name__ == "__main__":
    draw_system_architecture()
    draw_crisp_dm()
    draw_dfd()
    draw_etl_flowchart()
    draw_model_comparison()
    draw_streaming_pipeline()
    draw_dataset_schema()
    draw_tech_stack()
    print("\n[Diagrams] All 8 diagrams generated successfully in report/diagrams/")

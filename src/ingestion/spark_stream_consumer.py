"""
spark_stream_consumer.py
------------------------
Simulates a real-time Spark Structured Streaming consumer.
Performs rolling windowed power aggregations and detects transformer overload peaks.
"""

import os
import json
import time

def process_stream_batch(streaming_file="data/streaming/live_stream_buffer.jsonl"):
    if not os.path.exists(streaming_file):
        print(f"[Stream Consumer] No active buffer found at '{streaming_file}'.")
        return
        
    print("[Stream Consumer] Reading streaming buffer events...")
    total_draw_kw = 0.0
    active_ports = 0
    overload_alerts = []
    
    with open(streaming_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            evt = json.loads(line.strip())
            total_draw_kw += evt.get("current_power_draw_kw", 0.0)
            if evt.get("is_occupied"):
                active_ports += 1
            if evt.get("current_power_draw_kw", 0) > 45.0:
                overload_alerts.append(f"High Draw Warning: {evt['station_name']} Port #{evt['port_number']} drawing {evt['current_power_draw_kw']} kW")
                
    print(f"\n================ STREAM AGGREGATION SUMMARY ================")
    print(f"Total Instantaneous Grid Draw : {total_draw_kw:.2f} kW")
    print(f"Active Connected Ports        : {active_ports}")
    print(f"Total Alerts Triggered        : {len(overload_alerts)}")
    for a in overload_alerts[:3]:
        print(f"  [ALERT] {a}")
    print(f"============================================================")

if __name__ == "__main__":
    process_stream_batch()


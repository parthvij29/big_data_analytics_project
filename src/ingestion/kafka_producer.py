"""
kafka_producer.py
-----------------
Simulates real-time streaming telemetry and charging session plug-in events.
Can emit messages to an Apache Kafka topic or to a local streaming file buffer.
"""

import time
import json
import random
import datetime
import os
import sys

STATIONS = [
    {"name": "Boulder Junction Hub", "lat": 40.0212, "lon": -105.2514, "ports": 4, "type": "DC Fast", "cap_kw": 200},
    {"name": "Pearl Street Parking Garage", "lat": 40.0185, "lon": -105.2755, "ports": 6, "type": "Level 2", "cap_kw": 43.2},
    {"name": "Table Mesa Park-n-Ride", "lat": 39.9831, "lon": -105.2476, "ports": 8, "type": "DC Fast", "cap_kw": 400},
    {"name": "Alpine-Balsam Community Hub", "lat": 40.0271, "lon": -105.2812, "ports": 4, "type": "Level 2", "cap_kw": 28.8}
]

def generate_telemetry_event():
    station = random.choice(STATIONS)
    port_id = random.randint(1, station["ports"])
    is_active = random.choice([True, True, True, False])
    
    if is_active:
        current_kw = round(random.uniform(25.0, 50.0) if station["type"] == "DC Fast" else random.uniform(3.3, 7.2), 2)
        soc_pct = random.randint(15, 95)
    else:
        current_kw = 0.0
        soc_pct = 0
        
    event = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "station_name": station["name"],
        "port_number": port_id,
        "port_type": station["type"],
        "is_occupied": is_active,
        "current_power_draw_kw": current_kw,
        "battery_soc_pct": soc_pct,
        "latitude": station["lat"],
        "longitude": station["lon"]
    }
    return event

def stream_events(num_events=50, delay_sec=0.2, output_dir="data/streaming"):
    os.makedirs(output_dir, exist_ok=True)
    buffer_file = os.path.join(output_dir, "live_stream_buffer.jsonl")
    
    print(f"[Stream Producer] Starting telemetry generation ({num_events} events)...")
    
    with open(buffer_file, "a", encoding="utf-8") as f:
        for i in range(num_events):
            evt = generate_telemetry_event()
            f.write(json.dumps(evt) + "\n")
            f.flush()
            if (i + 1) % 10 == 0 or i == num_events - 1:
                print(f"[Stream Producer] Streamed event {i+1}/{num_events}: {evt['station_name']} -> {evt['current_power_draw_kw']} kW")
            time.sleep(delay_sec)
            
    print(f"[Stream Producer] Finished streaming. Live buffer saved to '{buffer_file}'.")

if __name__ == "__main__":
    stream_events()


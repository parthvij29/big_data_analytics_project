"""
kafka_producer.py
-----------------
Simulates real-time streaming telemetry and charging session plug-in events
for Indian EV charging networks (focusing on Greater Noida / Delhi-NCR around Bennett University).
Can emit messages to an Apache Kafka topic or to a local streaming file buffer.
"""

import time
import json
import random
import datetime
import os
import sys

STATIONS = [
    {"name": "Tata Power EZ Charge - Bennett University Campus", "lat": 28.4506, "lon": 77.5842, "ports": 6, "type": "DC Fast", "cap_kw": 360},
    {"name": "Statiq HyperCharge - Pari Chowk Metro Hub", "lat": 28.4650, "lon": 77.5100, "ports": 8, "type": "DC Fast", "cap_kw": 480},
    {"name": "BluSmart FastHub - Noida Expressway Sector 137", "lat": 28.5135, "lon": 77.4042, "ports": 8, "type": "DC Fast", "cap_kw": 480},
    {"name": "Jio-bp pulse - Knowledge Park II Station", "lat": 28.4620, "lon": 77.4950, "ports": 4, "type": "Level 2", "cap_kw": 88},
    {"name": "Fortum Charge & Drive - DLF Mall of India Sector 18", "lat": 28.5672, "lon": 77.3209, "ports": 8, "type": "DC Fast", "cap_kw": 480}
]

def generate_telemetry_event():
    station = random.choice(STATIONS)
    port_id = random.randint(1, station["ports"])
    is_active = random.choice([True, True, True, False])
    
    if is_active:
        current_kw = round(random.uniform(30.0, 58.0) if station["type"] == "DC Fast" else random.uniform(5.5, 7.2), 2)
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
    
    print(f"[Stream Producer] Starting Indian telemetry generation ({num_events} events)...")
    
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

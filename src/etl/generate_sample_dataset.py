"""
generate_sample_dataset.py
--------------------------
Generates realistic, schema-accurate Electric Vehicle Charging Station
Energy Consumption data matching the City of Boulder Open Data schema.

Columns:
- Station_Name: Name of the facility / charging hub
- Address: Street address
- City: City (Boulder)
- State: CO
- Postal_Code: ZIP Code
- Latitude: Double
- Longitude: Double
- Start_Date_Time: Timestamp (YYYY-MM-DD HH:MM:SS)
- End_Date_Time: Timestamp (YYYY-MM-DD HH:MM:SS)
- Total_Duration_hh_mm_ss: HH:MM:SS
- Charging_Time_hh_mm_ss: HH:MM:SS
- Energy__kWh_: Energy transferred in kilowatt-hours
- Port_Type: Level 2 / DC Fast
- Port_Number: 1 or 2
- User_ID: Anonymized driver ID
"""

import os
import random
import datetime
import csv

# Realistic Boulder charging hub locations
STATIONS = [
    {"name": "Boulder Junction Hub", "addr": "2180 Junction Pl", "lat": 40.0212, "lon": -105.2514, "ports": 4, "type": "DC Fast"},
    {"name": "Pearl Street Parking Garage", "addr": "1500 Pearl St", "lat": 40.0185, "lon": -105.2755, "ports": 6, "type": "Level 2"},
    {"name": "Alpine-Balsam Community Hub", "addr": "1136 Alpine Ave", "lat": 40.0271, "lon": -105.2812, "ports": 4, "type": "Level 2"},
    {"name": "Valmont City Park Station", "addr": "5275 Valmont Rd", "lat": 40.0289, "lon": -105.2185, "ports": 2, "type": "Level 2"},
    {"name": "Table Mesa Park-n-Ride", "addr": "5170 Table Mesa Dr", "lat": 39.9831, "lon": -105.2476, "ports": 8, "type": "DC Fast"},
    {"name": "Chautauqua Ranger Station", "addr": "900 Baseline Rd", "lat": 39.9989, "lon": -105.2829, "ports": 2, "type": "Level 2"},
    {"name": "East Boulder Community Center", "addr": "5660 Sioux Dr", "lat": 39.9965, "lon": -105.2223, "ports": 4, "type": "Level 2"},
    {"name": "CU Boulder Discovery Drive", "addr": "3400 Discovery Dr", "lat": 40.0105, "lon": -105.2442, "ports": 6, "type": "Level 2"},
    {"name": "Downtown 11th & Walnut Garage", "addr": "1100 Walnut St", "lat": 40.0162, "lon": -105.2818, "ports": 6, "type": "DC Fast"},
    {"name": "North Boulder Recreation Center", "addr": "3170 Broadway", "lat": 40.0335, "lon": -105.2789, "ports": 4, "type": "Level 2"}
]

USERS = [f"USR_{i:04d}" for i in range(1, 151)]

def format_duration(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def generate_dataset(num_records=5000, output_path="data/raw/boulder_ev_charging_data.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    start_date = datetime.datetime(2026, 1, 1, 6, 0, 0)
    records = []
    
    for _ in range(num_records):
        st = random.choice(STATIONS)
        port_num = random.randint(1, st["ports"])
        user_id = random.choice(USERS)
        
        # Stagger sessions across a 60-day window
        day_offset = random.randint(0, 60)
        # Higher density during peak commuting hours (7-9 AM, 12-2 PM, 5-8 PM)
        hour_weights = [1, 1, 1, 1, 2, 4, 8, 14, 15, 10, 8, 12, 14, 11, 9, 10, 13, 16, 17, 12, 8, 5, 3, 2]
        session_hour = random.choices(range(24), weights=hour_weights)[0]
        session_minute = random.randint(0, 59)
        session_second = random.randint(0, 59)
        
        session_start = start_date + datetime.timedelta(days=day_offset, hours=session_hour, minutes=session_minute, seconds=session_second)
        
        # Duration: DC Fast (20-60 min), Level 2 (1.5 - 6 hours)
        if st["type"] == "DC Fast":
            charging_secs = random.randint(20 * 60, 60 * 60)
            total_secs = charging_secs + random.randint(5 * 60, 20 * 60) # idle dwell
            energy_kwh = round((charging_secs / 3600.0) * random.uniform(35.0, 75.0), 2)
        else:
            charging_secs = random.randint(90 * 60, 300 * 60)
            total_secs = charging_secs + random.randint(10 * 60, 90 * 60)
            energy_kwh = round((charging_secs / 3600.0) * random.uniform(6.0, 11.0), 2)
            
        session_end = session_start + datetime.timedelta(seconds=total_secs)
        
        # Add slight spatial variance around station coordinates
        lat = round(st["lat"] + random.uniform(-0.0003, 0.0003), 6)
        lon = round(st["lon"] + random.uniform(-0.0003, 0.0003), 6)
        
        records.append({
            "Station_Name": st["name"],
            "Address": st["addr"],
            "City": "Boulder",
            "State": "CO",
            "Postal_Code": "80301",
            "Latitude": lat,
            "Longitude": lon,
            "Start_Date_Time": session_start.strftime("%Y-%m-%d %H:%M:%S"),
            "End_Date_Time": session_end.strftime("%Y-%m-%d %H:%M:%S"),
            "Total_Duration_hh_mm_ss": format_duration(total_secs),
            "Charging_Time_hh_mm_ss": format_duration(charging_secs),
            "Total_Duration_Minutes": round(total_secs / 60.0, 2),
            "Charging_Duration_Minutes": round(charging_secs / 60.0, 2),
            "Energy__kWh_": energy_kwh,
            "Port_Type": st["type"],
            "Port_Number": port_num,
            "User_ID": user_id
        })
        
    # Sort chronological by start time
    records.sort(key=lambda r: r["Start_Date_Time"])
    
    headers = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Successfully generated {len(records)} charging sessions to '{output_path}'.")

if __name__ == "__main__":
    generate_dataset(5000, "data/raw/boulder_ev_charging_data.csv")


"""
generate_sample_dataset.py
--------------------------
Generates realistic, schema-accurate Electric Vehicle Charging Station
Energy Consumption dataset for India (focusing on Delhi-NCR & Greater Noida around Bennett University).

Columns:
- Station_Name: Name of the Indian facility / charging hub
- Address: Street address
- City: Greater Noida / Noida / New Delhi / Gurugram
- State: UP / DL / HR
- Postal_Code: PIN Code
- Latitude: Double (WGS 84)
- Longitude: Double (WGS 84)
- Start_Date_Time: Timestamp (YYYY-MM-DD HH:MM:SS)
- End_Date_Time: Timestamp (YYYY-MM-DD HH:MM:SS)
- Total_Duration_hh_mm_ss: HH:MM:SS
- Charging_Time_hh_mm_ss: HH:MM:SS
- Total_Duration_Minutes: Double
- Charging_Duration_Minutes: Double
- Energy__kWh_: Energy transferred in kilowatt-hours
- Port_Type: DC Fast / Level 2
- Port_Number: 1, 2, 3, ...
- User_ID: Anonymized driver ID (e.g. DL_EV_0042)
"""

import os
import random
import datetime
import csv

# Authentic Indian EV charging hubs in Delhi-NCR / Greater Noida (Centered around Bennett University)
INDIAN_STATIONS = [
    {
        "name": "Tata Power EZ Charge - Bennett University Campus",
        "addr": "Plot Nos 8-11, TechZone II, Greater Noida",
        "city": "Greater Noida",
        "state": "UP",
        "postal": "201310",
        "lat": 28.4506,
        "lon": 77.5842,
        "ports": 6,
        "type": "DC Fast",
        "operator": "Tata Power EZ Charge",
        "power_kw": 60.0
    },
    {
        "name": "Statiq HyperCharge - Pari Chowk Metro Hub",
        "addr": "Pari Chowk Commercial Hub, Greater Noida",
        "city": "Greater Noida",
        "state": "UP",
        "postal": "201310",
        "lat": 28.4650,
        "lon": 77.5100,
        "ports": 8,
        "type": "DC Fast",
        "operator": "Statiq",
        "power_kw": 120.0
    },
    {
        "name": "Jio-bp pulse - Knowledge Park II Station",
        "addr": "Knowledge Park II Institutional Area, Greater Noida",
        "city": "Greater Noida",
        "state": "UP",
        "postal": "201306",
        "lat": 28.4620,
        "lon": 77.4950,
        "ports": 4,
        "type": "Level 2",
        "operator": "Jio-bp pulse",
        "power_kw": 22.0
    },
    {
        "name": "BluSmart FastHub - Noida Expressway Sector 137",
        "addr": "Sector 137 Metro Station, Noida Expressway",
        "city": "Noida",
        "state": "UP",
        "postal": "201305",
        "lat": 28.5135,
        "lon": 77.4042,
        "ports": 8,
        "type": "DC Fast",
        "operator": "BluSmart",
        "power_kw": 120.0
    },
    {
        "name": "Tata Power Superfast - Advant Navis Sector 142",
        "addr": "Advant Navis Business Park, Sector 142, Noida Expressway",
        "city": "Noida",
        "state": "UP",
        "postal": "201305",
        "lat": 28.4988,
        "lon": 77.4190,
        "ports": 6,
        "type": "DC Fast",
        "operator": "Tata Power EZ Charge",
        "power_kw": 60.0
    },
    {
        "name": "Fortum Charge & Drive - DLF Mall of India Sector 18",
        "addr": "Sector 18 Commercial Hub, Noida",
        "city": "Noida",
        "state": "UP",
        "postal": "201301",
        "lat": 28.5672,
        "lon": 77.3209,
        "ports": 8,
        "type": "DC Fast",
        "operator": "Fortum",
        "power_kw": 60.0
    },
    {
        "name": "Statiq EV Station - Electronic City Sector 62",
        "addr": "Sector 62 IT Park, Noida",
        "city": "Noida",
        "state": "UP",
        "postal": "201309",
        "lat": 28.6280,
        "lon": 77.3649,
        "ports": 6,
        "type": "Level 2",
        "operator": "Statiq",
        "power_kw": 22.0
    },
    {
        "name": "Jio-bp pulse - Gaur City Mall Hub (Gr Noida West)",
        "addr": "Char Murti Chowk, Gaur City 1, Greater Noida West",
        "city": "Greater Noida",
        "state": "UP",
        "postal": "201009",
        "lat": 28.6080,
        "lon": 77.4260,
        "ports": 6,
        "type": "DC Fast",
        "operator": "Jio-bp pulse",
        "power_kw": 60.0
    },
    {
        "name": "BSES EV Fast Charging Plaza - Connaught Place",
        "addr": "Inner Circle, Connaught Place, New Delhi",
        "city": "New Delhi",
        "state": "DL",
        "postal": "110001",
        "lat": 28.6315,
        "lon": 77.2167,
        "ports": 8,
        "type": "DC Fast",
        "operator": "BSES",
        "power_kw": 150.0
    },
    {
        "name": "BluSmart Supercharger - Aerocity IGI Airport",
        "addr": "Hospitality District, Aerocity, New Delhi",
        "city": "New Delhi",
        "state": "DL",
        "postal": "110037",
        "lat": 28.5562,
        "lon": 77.1000,
        "ports": 10,
        "type": "DC Fast",
        "operator": "BluSmart",
        "power_kw": 180.0
    },
    {
        "name": "Statiq CyberHub - DLF Phase 2 Gurugram",
        "addr": "Cyber City Rapid Metro, Gurugram",
        "city": "Gurugram",
        "state": "HR",
        "postal": "122002",
        "lat": 28.4950,
        "lon": 77.0890,
        "ports": 8,
        "type": "DC Fast",
        "operator": "Statiq",
        "power_kw": 120.0
    },
    {
        "name": "Tata Power AC Hub - Okhla Phase III",
        "addr": "Okhla Industrial Area Phase III, New Delhi",
        "city": "New Delhi",
        "state": "DL",
        "postal": "110020",
        "lat": 28.5412,
        "lon": 77.2721,
        "ports": 4,
        "type": "Level 2",
        "operator": "Tata Power EZ Charge",
        "power_kw": 22.0
    }
]

USERS = [f"IN_EV_{i:04d}" for i in range(1, 151)]

def format_duration(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def generate_dataset(num_records=5000, output_path="data/raw/boulder_ev_charging_data.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    start_date = datetime.datetime(2026, 1, 1, 6, 0, 0)
    records = []
    
    random.seed(42)
    
    for _ in range(num_records):
        st = random.choice(INDIAN_STATIONS)
        port_num = random.randint(1, st["ports"])
        user = random.choice(USERS)
        
        # Random timestamp over 90 days
        delta_days = random.randint(0, 90)
        
        # Rush hour distribution in Indian metropolitan traffic:
        # Peak 1: 08:00 - 11:30 (Morning Commute)
        # Peak 2: 17:30 - 21:30 (Evening Commute)
        hour_weights = [
            1, 1, 1, 1, 2, 4,       # 00:00 - 05:00
            8, 15, 20, 18, 14, 12,  # 06:00 - 11:00
            12, 10, 10, 12, 16, 22, # 12:00 - 17:00
            25, 20, 15, 10, 6, 3    # 18:00 - 23:00
        ]
        hour = random.choices(range(24), weights=hour_weights)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        sess_start = start_date + datetime.timedelta(days=delta_days, hours=hour, minutes=minute, seconds=second)
        
        # Battery specs (Nexon EV 30-40 kWh, Tiago EV 19-24 kWh, ZS EV 50 kWh, Ioniq 5 72 kWh)
        if st["type"] == "DC Fast":
            # 25 min to 65 min charging duration
            active_charge_sec = random.randint(25 * 60, 65 * 60)
            dwell_sec = active_charge_sec + random.randint(5 * 60, 20 * 60)
            energy_kwh = round(random.uniform(22.0, 52.0), 2)
        else:
            # Level 2 AC: 1.5 to 5 hours
            active_charge_sec = random.randint(90 * 60, 240 * 60)
            dwell_sec = active_charge_sec + random.randint(15 * 60, 60 * 60)
            energy_kwh = round(random.uniform(14.0, 32.0), 2)
            
        sess_end = sess_start + datetime.timedelta(seconds=dwell_sec)
        
        records.append({
            "Station_Name": st["name"],
            "Address": st["addr"],
            "City": st["city"],
            "State": st["state"],
            "Postal_Code": st["postal"],
            "Latitude": st["lat"],
            "Longitude": st["lon"],
            "Start_Date_Time": sess_start.strftime("%Y-%m-%d %H:%M:%S"),
            "End_Date_Time": sess_end.strftime("%Y-%m-%d %H:%M:%S"),
            "Total_Duration_hh_mm_ss": format_duration(dwell_sec),
            "Charging_Time_hh_mm_ss": format_duration(active_charge_sec),
            "Total_Duration_Minutes": round(dwell_sec / 60.0, 2),
            "Charging_Duration_Minutes": round(active_charge_sec / 60.0, 2),
            "Energy__kWh_": energy_kwh,
            "Port_Type": st["type"],
            "Port_Number": port_num,
            "User_ID": user
        })
        
    fieldnames = [
        "Station_Name", "Address", "City", "State", "Postal_Code",
        "Latitude", "Longitude", "Start_Date_Time", "End_Date_Time",
        "Total_Duration_hh_mm_ss", "Charging_Time_hh_mm_ss",
        "Total_Duration_Minutes", "Charging_Duration_Minutes",
        "Energy__kWh_", "Port_Type", "Port_Number", "User_ID"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"[DataGen] Successfully generated {len(records)} authentic Indian EV charging records.")
    print(f"[DataGen] Saved to: {output_path}")

if __name__ == "__main__":
    generate_dataset()

"""
kafka_producer.py
-----------------
Simulates real-time streaming telemetry and charging session plug-in events
for Indian EV charging networks (focusing on Greater Noida / Delhi-NCR around Bennett University),
and fetches real live weather/solar telemetry from the Open-Meteo API.

Supports dual-mode delivery:
1. Live Apache Kafka broker (via kafka-python KafkaProducer) when reachable.
2. Portable local JSONL buffer fallback when Kafka is unavailable.
"""

import time
import json
import random
import datetime
import os
import urllib.request

STATIONS = [
    {"name": "Tata Power EZ Charge - Bennett University Campus", "lat": 28.4506, "lon": 77.5842, "ports": 6, "type": "DC Fast", "cap_kw": 360},
    {"name": "Statiq HyperCharge - Pari Chowk Metro Hub", "lat": 28.4650, "lon": 77.5100, "ports": 8, "type": "DC Fast", "cap_kw": 480},
    {"name": "BluSmart FastHub - Noida Expressway Sector 137", "lat": 28.5135, "lon": 77.4042, "ports": 8, "type": "DC Fast", "cap_kw": 480},
    {"name": "Jio-bp pulse - Knowledge Park II Station", "lat": 28.4620, "lon": 77.4950, "ports": 4, "type": "Level 2", "cap_kw": 88},
    {"name": "Fortum Charge & Drive - DLF Mall of India Sector 18", "lat": 28.5672, "lon": 77.3209, "ports": 8, "type": "DC Fast", "cap_kw": 480}
]


def _create_kafka_producer(bootstrap_servers="localhost:9092"):
    """Return a live KafkaProducer if kafka-python and broker are available, else None."""
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            request_timeout_ms=3000,
        )
        return producer
    except Exception as exc:
        print(f"[Kafka Producer] Broker unavailable ({exc}). Using local JSONL fallback.")
        return None


def fetch_live_weather_event(city="Noida", lat=28.5355, lon=77.3910):
    """Fetch real-time ambient temperature and solar irradiance from Open-Meteo."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_10m"
        "&timezone=Asia%2FKolkata"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        cur = payload.get("current", {})
        return {
            "event_type": "weather_telemetry",
            "city": city,
            "timestamp": cur.get("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "temperature_c": cur.get("temperature_2m"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "solar_irradiance_wm2": cur.get("shortwave_radiation"),
            "wind_speed_kmh": cur.get("wind_speed_10m"),
            "source": "open-meteo.com",
        }
    except Exception as exc:
        print(f"[Weather Producer] Open-Meteo fetch skipped ({exc}).")
        return None


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

    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "station_name": station["name"],
        "port_number": port_id,
        "port_type": station["type"],
        "is_occupied": is_active,
        "current_power_draw_kw": current_kw,
        "battery_soc_pct": soc_pct,
        "latitude": station["lat"],
        "longitude": station["lon"],
    }


def publish_weather_snapshot(
    output_dir="data/streaming",
    bootstrap_servers="localhost:9092",
    weather_topic="voltpulse-weather-telemetry",
    city="Noida",
    lat=28.5355,
    lon=77.3910,
):
    """Publish a real Open-Meteo weather/solar event to Kafka or local weather JSONL buffer."""
    evt = fetch_live_weather_event(city=city, lat=lat, lon=lon)
    if not evt:
        return None

    producer = _create_kafka_producer(bootstrap_servers)
    if producer is not None:
        producer.send(weather_topic, value=json.dumps(evt).encode("utf-8"))
        producer.flush()
        producer.close()
        print(f"[Kafka Producer] Published live weather event to topic '{weather_topic}'.")
        return evt

    os.makedirs(output_dir, exist_ok=True)
    weather_file = os.path.join(output_dir, "weather_stream_buffer.jsonl")
    with open(weather_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(evt) + "\n")
    print(f"[Weather Producer] Saved live Open-Meteo event to '{weather_file}'.")
    return evt


def stream_events(
    num_events=50,
    delay_sec=0.2,
    output_dir="data/streaming",
    bootstrap_servers="localhost:9092",
    topic="voltpulse-ev-telemetry",
    weather_topic="voltpulse-weather-telemetry",
    include_weather=True,
):
    os.makedirs(output_dir, exist_ok=True)
    buffer_file = os.path.join(output_dir, "live_stream_buffer.jsonl")

    if include_weather:
        publish_weather_snapshot(
            output_dir=output_dir,
            bootstrap_servers=bootstrap_servers,
            weather_topic=weather_topic,
        )

    producer = _create_kafka_producer(bootstrap_servers)
    print(f"[Stream Producer] Starting Indian telemetry generation ({num_events} events)...")

    if producer is not None:
        try:
            for i in range(num_events):
                evt = generate_telemetry_event()
                producer.send(topic, key=evt["station_name"].encode("utf-8"), value=json.dumps(evt).encode("utf-8"))
                if (i + 1) % 10 == 0 or i == num_events - 1:
                    print(f"[Kafka Producer] Sent event {i+1}/{num_events} to '{topic}': {evt['station_name']} -> {evt['current_power_draw_kw']} kW")
                time.sleep(delay_sec)
            producer.flush()
            print(f"[Kafka Producer] Finished streaming {num_events} events to Kafka topic '{topic}'.")
            return
        finally:
            producer.close()

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

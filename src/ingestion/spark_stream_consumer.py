"""
spark_stream_consumer.py
------------------------
Dual-mode stream consumer for VoltPulse:
1. Consumes from live Apache Kafka topics ('voltpulse-ev-telemetry' and
   'voltpulse-weather-telemetry') when kafka-python and a broker are reachable.
2. Falls back to replaying the saved JSONL stream buffers
   ('data/streaming/live_stream_buffer.jsonl' and optional 'weather_stream_buffer.jsonl'),
   aggregating power draw, occupancy, >45 kW overload alerts, and weather/solar grid context.
"""

import os
import json


def _consume_from_kafka(bootstrap_servers="localhost:9092", topic="voltpulse-ev-telemetry", weather_topic="voltpulse-weather-telemetry"):
    """Attempt to read buffered events from live Kafka topics; return (events, latest_weather) or (None, None)."""
    try:
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=1500,
        )
        events = [json.loads(msg.value.decode("utf-8")) for msg in consumer]
        consumer.close()

        latest_weather = None
        w_consumer = KafkaConsumer(
            weather_topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=1000,
        )
        for msg in w_consumer:
            latest_weather = json.loads(msg.value.decode("utf-8"))
        w_consumer.close()
        return events, latest_weather
    except Exception as exc:
        print(f"[Stream Consumer] Kafka broker unavailable ({exc}). Using local JSONL replay fallback.")
        return None, None


def _read_latest_weather_jsonl(weather_file="data/streaming/weather_stream_buffer.jsonl"):
    if not os.path.exists(weather_file):
        return None
    latest = None
    with open(weather_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                latest = json.loads(line.strip())
    return latest


def process_stream_batch(
    streaming_file="data/streaming/live_stream_buffer.jsonl",
    weather_file="data/streaming/weather_stream_buffer.jsonl",
    bootstrap_servers="localhost:9092",
    topic="voltpulse-ev-telemetry",
    weather_topic="voltpulse-weather-telemetry",
):
    events, latest_weather = _consume_from_kafka(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        weather_topic=weather_topic,
    )

    if events is None:
        if not os.path.exists(streaming_file):
            print(f"[Stream Consumer] No active buffer found at '{streaming_file}'.")
            return
        print("[Stream Consumer] Reading streaming buffer events...")
        events = []
        with open(streaming_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line.strip()))
        latest_weather = _read_latest_weather_jsonl(weather_file)

    total_draw_kw = 0.0
    active_ports = 0
    overload_alerts = []

    for evt in events:
        total_draw_kw += evt.get("current_power_draw_kw", 0.0)
        if evt.get("is_occupied"):
            active_ports += 1
        if evt.get("current_power_draw_kw", 0) > 45.0:
            overload_alerts.append(
                f"High Draw Warning: {evt['station_name']} Port #{evt['port_number']} drawing {evt['current_power_draw_kw']} kW"
            )

    print(f"\n================ STREAM AGGREGATION SUMMARY ================")
    print(f"Sum of Event Power Values    : {total_draw_kw:.2f} kW")
    print(f"Occupied Event Rows          : {active_ports}")
    print(f"Events Above 45 kW           : {len(overload_alerts)}")
    for a in overload_alerts[:3]:
        print(f"  [ALERT] {a}")

    if latest_weather:
        temp = latest_weather.get("temperature_c")
        solar = latest_weather.get("solar_irradiance_wm2")
        city = latest_weather.get("city", "Noida")
        stress = "Normal"
        if temp is not None and temp >= 35:
            stress = "High Thermal Load (>=35 C)"
        elif solar is not None and solar >= 400:
            stress = "Solar-Assisted Daytime Window"
        elif solar is not None and solar < 20:
            stress = "Full Grid Dependency (Low Solar)"
        print(f"------------------------------------------------------------")
        print(f"Live Weather Stream ({city})  : {temp} C | Solar {solar} W/m2 | {stress}")

    print(f"============================================================")


if __name__ == "__main__":
    process_stream_batch()

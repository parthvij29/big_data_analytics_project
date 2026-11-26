"""
server.py
---------
Threaded HTTP Server serving the VoltPulse UI on port 3000,
plus live Apache Kafka stream endpoints (/api/stream and /api/stream/produce)
with graceful fallback when Kafka is unavailable.
"""

import http.server
import json
import os
import sys
import threading
import time

PORT = 3000
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(WEB_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

KAFKA_BOOTSTRAP = os.environ.get("VOLTPULSE_KAFKA_BOOTSTRAP", "localhost:9092")
EV_TOPIC = "voltpulse-ev-telemetry"
WEATHER_TOPIC = "voltpulse-weather-telemetry"


class LiveKafkaState:
    def __init__(self):
        self.lock = threading.Lock()
        self.connected = False
        self.error = "Starting Kafka consumer..."
        self.events = []
        self.total_power_kw = 0.0
        self.occupied_ports = 0
        self.alerts = []
        self.latest_weather = None

    def add_ev_event(self, evt):
        with self.lock:
            self.events.append(evt)
            kw = float(evt.get("current_power_draw_kw", 0.0))
            self.total_power_kw = round(self.total_power_kw + kw, 2)
            if evt.get("is_occupied"):
                self.occupied_ports += 1
            if kw > 45.0:
                self.alerts.append({
                    "t": str(evt.get("timestamp", "")).split(" ")[-1],
                    "station": evt.get("station_name", ""),
                    "port": evt.get("port_number", 0),
                    "kw": kw,
                })
            if len(self.events) > 500:
                self.events = self.events[-500:]
            if len(self.alerts) > 50:
                self.alerts = self.alerts[-50:]

    def snapshot(self):
        with self.lock:
            return {
                "source": "kafka" if self.connected else "unavailable",
                "broker": KAFKA_BOOTSTRAP,
                "topic": EV_TOPIC,
                "error": None if self.connected else self.error,
                "events_count": len(self.events),
                "total_power_kw": self.total_power_kw,
                "occupied_ports": self.occupied_ports,
                "alerts_count": len(self.alerts),
                "alerts": list(self.alerts[-10:]),
                "latest_event": self.events[-1] if self.events else None,
                "latest_weather": self.latest_weather,
            }


kafka_state = LiveKafkaState()


def _kafka_consumer_loop():
    while True:
        try:
            from kafka import KafkaConsumer
            consumer = KafkaConsumer(
                EV_TOPIC,
                WEATHER_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                consumer_timeout_ms=1000,
            )
            with kafka_state.lock:
                kafka_state.connected = True
                kafka_state.error = None
                kafka_state.events.clear()
                kafka_state.total_power_kw = 0.0
                kafka_state.occupied_ports = 0
                kafka_state.alerts.clear()

            while True:
                records = consumer.poll(timeout_ms=1000)
                for tp, msgs in records.items():
                    for msg in msgs:
                        val = json.loads(msg.value.decode("utf-8"))
                        if tp.topic == EV_TOPIC:
                            kafka_state.add_ev_event(val)
                        elif tp.topic == WEATHER_TOPIC:
                            with kafka_state.lock:
                                kafka_state.latest_weather = val
        except Exception as exc:
            with kafka_state.lock:
                kafka_state.connected = False
                kafka_state.error = str(exc)
            time.sleep(3)


class ReusableThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/stream":
            self._send_json(200, kafka_state.snapshot())
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] == "/api/stream/produce":
            try:
                from src.ingestion.kafka_producer import stream_events
                threading.Thread(
                    target=stream_events,
                    kwargs={"num_events": 10, "delay_sec": 0.35, "bootstrap_servers": KAFKA_BOOTSTRAP, "include_weather": False},
                    daemon=True,
                ).start()
                self._send_json(202, {"status": "streaming", "count": 10, "topic": EV_TOPIC, "broker": KAFKA_BOOTSTRAP})
            except Exception as exc:
                self._send_json(500, {"status": "error", "error": str(exc)})
            return
        self.send_error(404)


def run_server():
    threading.Thread(target=_kafka_consumer_loop, daemon=True).start()
    os.chdir(WEB_DIR)
    with ReusableThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"[VoltPulse Modern UI] Server running at http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()

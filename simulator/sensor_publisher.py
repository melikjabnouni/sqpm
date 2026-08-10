import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC_CYCLE = "sqpm/line1/cycle"
TOPIC_DOWNTIME = "sqpm/line1/downtime"
TOPIC_QUALITY = "sqpm/line1/quality"

IDEAL_CYCLE_TIME_S = 5.0   # target seconds per unit, tweak to taste
QUALITY_TARGET = 100.0     # e.g. a dimension in mm, control chart centers here
QUALITY_SIGMA = 1.5        # normal-process noise
DEFECT_RATE = 0.06         # fraction of units that fail quality check


def make_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    return client


def publish_cycle_event(client, unit_id):
    jitter = random.gauss(0, 0.4)
    slowdown = random.choice([0, 0, 0, 0, 3.0])  # rare slow cycles
    cycle_time = max(0.5, IDEAL_CYCLE_TIME_S + jitter + slowdown)

    payload = {
        "unit_id": unit_id,
        "cycle_time_s": round(cycle_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    client.publish(TOPIC_CYCLE, json.dumps(payload))
    return cycle_time


def publish_quality_event(client, unit_id):
    measurement = random.gauss(QUALITY_TARGET, QUALITY_SIGMA)
    is_defect = random.random() < DEFECT_RATE
    if is_defect:
        measurement += random.choice([-1, 1]) * random.uniform(4, 8)

    payload = {
        "unit_id": unit_id,
        "measurement": round(measurement, 3),
        "pass": not is_defect,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    client.publish(TOPIC_QUALITY, json.dumps(payload))


def maybe_publish_downtime(client):
    if random.random() < 0.03:
        duration_s = random.uniform(10, 90)
        payload = {
            "duration_s": round(duration_s, 1),
            "reason": random.choice(
                ["jam", "changeover", "sensor_fault", "operator_break"]
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        client.publish(TOPIC_DOWNTIME, json.dumps(payload))
        print(f"[downtime] {payload}")
        time.sleep(duration_s / 10)


def main():
    client = make_client()
    unit_id = 0
    print("Publishing simulated line events. Ctrl+C to stop.")
    try:
        while True:
            unit_id += 1
            cycle_time = publish_cycle_event(client, unit_id)
            publish_quality_event(client, unit_id)
            print(f"[unit {unit_id}] cycle_time={cycle_time:.2f}s")
            maybe_publish_downtime(client)
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopping publisher.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
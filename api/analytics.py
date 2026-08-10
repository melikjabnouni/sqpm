import statistics
import threading
from collections import deque
from datetime import datetime, timezone


class LineDataStore:
    """
    Thread-safe rolling-window store for simulated production events.
    Written to by the MQTT callback thread, read from by FastAPI request threads.
    """

    def __init__(self, max_events=500):
        self._lock = threading.Lock()
        self.cycle_events = deque(maxlen=max_events)
        self.quality_events = deque(maxlen=max_events)
        self.downtime_events = deque(maxlen=max_events)

    def add_cycle_event(self, payload):
        with self._lock:
            self.cycle_events.append(payload)

    def add_quality_event(self, payload):
        with self._lock:
            self.quality_events.append(payload)

    def add_downtime_event(self, payload):
        with self._lock:
            self.downtime_events.append(payload)

    def snapshot(self):
        """Return a consistent copy of all three event lists at once."""
        with self._lock:
            return (
                list(self.cycle_events),
                list(self.quality_events),
                list(self.downtime_events),
            )


# Shared singleton instance — imported by both mqtt_consumer.py and main.py
store = LineDataStore()


IDEAL_CYCLE_TIME_S = 5.0  # must match simulator/sensor_publisher.py
# Customer/process spec limits for the quality measurement (Cp/Cpk).
# Distinct from UCL/LCL: these are external tolerance requirements, not
# statistically derived from the data itself.
USL = 106.0
LSL = 94.0

def compute_oee():
    cycle_events, quality_events, downtime_events = store.snapshot()

    if not cycle_events:
        return {
            "availability": None,
            "performance": None,
            "quality": None,
            "oee": None,
            "units_produced": 0,
            "message": "no data yet",
        }

    units_produced = len(cycle_events)

    # --- Availability: run time vs. planned time ---
    total_downtime_s = sum(e["duration_s"] for e in downtime_events)
    total_run_time_s = sum(e["cycle_time_s"] for e in cycle_events)
    planned_time_s = total_run_time_s + total_downtime_s
    availability = (
        (planned_time_s - total_downtime_s) / planned_time_s
        if planned_time_s > 0
        else 0
    )

    # --- Performance: ideal cycle time vs. actual ---
    ideal_total_s = IDEAL_CYCLE_TIME_S * units_produced
    performance = (
        ideal_total_s / total_run_time_s if total_run_time_s > 0 else 0
    )
    performance = min(performance, 1.0)  # cap at 100%, can't beat "ideal"

    # --- Quality: good units vs. total ---
    good_units = sum(1 for e in quality_events if e.get("pass"))
    quality = good_units / len(quality_events) if quality_events else 0

    oee = availability * performance * quality

    return {
        "availability": round(availability * 100, 1),
        "performance": round(performance * 100, 1),
        "quality": round(quality * 100, 1),
        "oee": round(oee * 100, 1),
        "units_produced": units_produced,
    }


def compute_spc():
    _, quality_events, _ = store.snapshot()

    if len(quality_events) < 2:
        return {
            "points": [], "center_line": None, "ucl": None, "lcl": None,
            "cp": None, "cpk": None, "usl": USL, "lsl": LSL,
            "message": "not enough data yet",
        }

    measurements = [e["measurement"] for e in quality_events]
    center_line = statistics.mean(measurements)
    std_dev = statistics.stdev(measurements)

    ucl = center_line + 3 * std_dev
    lcl = center_line - 3 * std_dev

    # --- Process capability indices ---
    if std_dev > 0:
        cp = (USL - LSL) / (6 * std_dev)
        cpu = (USL - center_line) / (3 * std_dev)  # capability re: upper spec
        cpl = (center_line - LSL) / (3 * std_dev)  # capability re: lower spec
        cpk = min(cpu, cpl)
    else:
        cp = None
        cpk = None

    points = [
        {
            "unit_id": e["unit_id"],
            "measurement": e["measurement"],
            "out_of_control": e["measurement"] > ucl or e["measurement"] < lcl,
            "timestamp": e["timestamp"],
        }
        for e in quality_events
    ]

    return {
        "points": points,
        "center_line": round(center_line, 3),
        "ucl": round(ucl, 3),
        "lcl": round(lcl, 3),
        "cp": round(cp, 3) if cp is not None else None,
        "cpk": round(cpk, 3) if cpk is not None else None,
        "usl": USL,
        "lsl": LSL,
    }
# beacon_encoder.py

import json
import os
import struct
import time

DATA_FILE = "main_running_data.json"

# ==============================
# BEACON FIELD DEFINITION TABLE
# ==============================
# This follows your uploaded table
BEACON_DEFINITION = [
    ("unix_time", "<I", lambda d: int(time.time())),
    ("packet_count", "<H", lambda d: d.get("packet_count", 0)),
    ("num_resets", "<H", lambda d: d.get("num_resets", 0)),
    ("gyro_x", "<h", lambda d: int(d.get("gyro_x", 0))),
    ("gyro_y", "<h", lambda d: int(d.get("gyro_y", 0))),
    ("gyro_z", "<h", lambda d: int(d.get("gyro_z", 0))),
    ("accel_x", "<h", lambda d: int(d.get("accel_x", 0))),
    ("accel_y", "<h", lambda d: int(d.get("accel_y", 0))),
    ("accel_z", "<h", lambda d: int(d.get("accel_z", 0))),
    ("mag_x", "<h", lambda d: int(d.get("mag_x", 0))),
    ("mag_y", "<h", lambda d: int(d.get("mag_y", 0))),
    ("mag_z", "<h", lambda d: int(d.get("mag_z", 0))),
    ("tmp1", "<h", lambda d: int(d.get("tmp1", 0))),
    ("tmp2", "<h", lambda d: int(d.get("tmp2", 0))),
    ("bme_temp", "<h", lambda d: int(d.get("bme_temp", 0) * 100)),
    ("bme_pressure", "<I", lambda d: int(d.get("bme_pressure", 0) * 100)),
    ("bme_humidity", "<H", lambda d: int(d.get("bme_humidity", 0) * 100)),
    ("used_memory", "<I", lambda d: int(d.get("used_memory", 0))),
    ("free_memory", "<I", lambda d: int(d.get("free_memory", 0))),
    ("used_disk", "<I", lambda d: int(d.get("used_disk", 0))),
    ("free_disk", "<I", lambda d: int(d.get("free_disk", 0))),
    ("cpu_load", "<H", lambda d: int(d.get("cpu_load", 0) * 100)),
    ("cpu_temp", "<h", lambda d: int(d.get("cpu_temp", 0) * 10)),
    ("batt_voltage", "<H", lambda d: int(d.get("batt_voltage", 0))),
    ("batt_current", "<H", lambda d: int(d.get("batt_current", 0))),
    ("v_3v3", "<H", lambda d: int(d.get("v_3v3", 0))),
    ("i_3v3", "<H", lambda d: int(d.get("i_3v3", 0))),
    ("v_5v0", "<H", lambda d: int(d.get("v_5v0", 0))),
    ("i_5v0", "<H", lambda d: int(d.get("i_5v0", 0))),
    ("v_vbatt", "<H", lambda d: int(d.get("v_vbatt", 0))),
    ("i_vbatt", "<H", lambda d: int(d.get("i_vbatt", 0))),
    ("reg_temp_3v3", "<h", lambda d: int(d.get("reg_temp_3v3", 0))),
    ("reg_temp_5v0", "<h", lambda d: int(d.get("reg_temp_5v0", 0))),
    ("gps_lat", "<i", lambda d: int(d.get("gps_lat", 0) * 1e7)),
    ("gps_lon", "<i", lambda d: int(d.get("gps_lon", 0) * 1e7)),
    ("gps_alt", "<I", lambda d: int(d.get("gps_alt", 0) * 1e5)),
    ("gps_velocity", "<H", lambda d: int(d.get("gps_velocity", 0) * 1000)),
    ("gps_num_sats", "<B", lambda d: int(d.get("gps_num_sats", 0))),
    ("rm3100_mag_x", "<i", lambda d: int(d.get("rm3100_mag_x", 0))),
    ("rm3100_mag_y", "<i", lambda d: int(d.get("rm3100_mag_y", 0))),
    ("rm3100_mag_z", "<i", lambda d: int(d.get("rm3100_mag_z", 0))),
]

# ==============================
# DATA HANDLING
# ==============================
def read_latest_json_data():
    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                latest_line = lines[-1]
                data = json.loads(latest_line)
                return data  # already one combined JSON
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {e}")
        return {}

# ==============================
# ENCODING
# ==============================
def create_beacon(sensor_data):
    beacon_bytes = b""
    for name, fmt, extractor in BEACON_DEFINITION:
        try:
            value = extractor(sensor_data)
            beacon_bytes += struct.pack(fmt, value)
        except Exception as e:
            print(f"Encoding error for {name}: {e}")
            beacon_bytes += b"\x00" * struct.calcsize(fmt)
    return beacon_bytes.hex().upper()


def run_beacon_encoder():
    data = read_latest_json_data()
    if not data:
        print("No sensor data available.")
        return
    beacon_hex = create_beacon(data)
    print(f"Beacon Encoded (HEX):\n{beacon_hex}\n")
    with open("beacon_output.txt", "a") as f:
        f.write(beacon_hex + "\n")


if __name__ == "__main__":
    run_beacon_encoder()

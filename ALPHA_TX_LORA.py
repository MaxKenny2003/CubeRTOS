# Imports
import time
import busio
import board
import adafruit_rfm9x
from encode import encode_rap
from digitalio import DigitalInOut, Direction, Pull

# beacon_encoder.py

import json
import os
import struct
import time
import base64

try:
   # DATA_FOLDER = "data/"
    DATA_FILE = "main_running_data.json"
except:
    folder_name = "data/"
   # os.mkdir(folder_name)
   #DATA_FOLDER = "data/"
    DATA_FILE = "main_running_data.json"

BEACON_DEFINITION = [
    ("unix_time", "<I", lambda d: int(time.time())),
    ("packet_count", "<H", lambda d: int(d.get("packet_count", 0))),
    ("num_resets", "<H", lambda d: int(d.get("num_resets", 0))),
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
    ("bme_temp", "<h", lambda d: int(d.get("bme_temp", 0) * 100)),     # °C → 100×
    ("bme_pressure", "<I", lambda d: int(d.get("bme_pressure", 0) * 100)),  # mbar → 100×
    ("bme_humidity", "<H", lambda d: int(d.get("bme_humidity", 0) * 100)),  # %RH → 100×
    ("used_memory", "<I", lambda d: int(d.get("used_memory", 0))),
    ("free_memory", "<I", lambda d: int(d.get("free_memory", 0))),
    ("used_disk", "<I", lambda d: int(d.get("used_disk", 0))),
    ("free_disk", "<I", lambda d: int(d.get("free_disk", 0))),
    ("cpu_load", "<H", lambda d: int(d.get("cpu_load", 0) * 100)),
    ("cpu_temp", "<h", lambda d: int(d.get("cpu_temp", 0) * 10)),  # °C → 10×
    # ===============================
    # Power section (match offsets exactly)
    # ===============================
    ("batt_voltage", "<H", lambda d: int((float(d.get("batt_voltage", 0.0)) * (12.0/(100.0+12.0))) / 2.5 * 4095)),  # scale depends on ADC ref (see below)
    ("batt_current", "<H", lambda d: int(float(d.get("batt_current", 0.0)) * (0.012*100.0) / 2.5 * 4095)),
    ("v_3v3", "<H", lambda d: int(float(d.get("v_3v3", 0.0)) * (60.4/(100.0+60.4)) / 2.5 * 4095)),
    ("i_3v3", "<H", lambda d: int(float(d.get("i_3v3", 0.0)) * (0.005*100.0) / 2.5 * 4095)),
    ("v_5v0", "<H", lambda d: int(float(d.get("v_5v0", 0.0)) * (33.2/(100.0+33.2)) / 2.5 * 4095)),
    ("i_5v0", "<H", lambda d: int(float(d.get("i_5v0", 0.0)) * (0.012*100.0) / 2.5 * 4095)),
    ("v_vbatt", "<H", lambda d: int(float(d.get("v_vbatt", 0.0)) * (12.0/(100.0+12.0)) / 2.5 * 4095)),
    ("i_vbatt", "<H", lambda d: int(float(d.get("i_vbatt", 0.0)) * (0.012*100.0) / 2.5 * 4095)),
    ("reg_temp_3v3", "<H", lambda d: int(max(0, min(4095, ((1.8639 - 3.88e-6 * (((float(d.get("reg_temp_3v3", 0.0)) + 1481.96)**2 - 2.1962e6))) / 2.5) * 4095)))),
    ("reg_temp_5v0", "<H", lambda d: int(max(0, min(4095, ((1.8639 - 3.88e-6 * (((float(d.get("reg_temp_5v0", 0.0)) + 1481.96)**2 - 2.1962e6))) / 2.5) * 4095)))),
    # ===============================
    # GPS
    # ===============================
    ("gps_lat", "<i", lambda d: int(d.get("gps_lat", 0) * 1e7)),
    ("gps_lon", "<i", lambda d: int(d.get("gps_lon", 0) * 1e7)),
    ("gps_alt", "<I", lambda d: int(d.get("gps_alt", 0) * 1e5)),
    ("gps_velocity", "<H", lambda d: int(d.get("gps_velocity", 0) * 1000)),
    ("gps_num_sats", "<B", lambda d: int(d.get("gps_num_sats", 0))),
    # ===============================
    # RM3100 Magnetometer
    # ===============================
    ("rm3100_mag_x", "<i", lambda d: int(d.get("rm3100_mag_x", 0))),
    ("rm3100_mag_y", "<i", lambda d: int(d.get("rm3100_mag_y", 0))),
    ("rm3100_mag_z", "<i", lambda d: int(d.get("rm3100_mag_z", 0))),
]


# ==============================
# DATA HANDLING
# ==============================
def read_latest_json_data():
    combined_data = {}
    # data_folder = "data/"
    # Load the current aggregate file first
    try:
        with open("main_running_data.json", "r") as f:
            data = json.load(f)
            combined_data.update(data)
    except Exception as e:
        print(f"Error reading main_running_data.json: {e}")

    # Overlay any fresh per-sensor JSONs (e.g., data/RM3100_data.json)
    try:
        if os.path.isdir("data"):
            for fn in os.listdir("data"):
                if fn.endswith(".json"):
                    path = os.path.join("data", fn)
                    try:
                        with open(path, "r") as f:
                            d = json.load(f)
                            combined_data.update(d)
                    except Exception as e:
                        print(f"Warning: could not decode JSON in {fn}: {e}")
    except Exception as e:
        print(f"Error scanning data/: {e}")

    return combined_data

    # filename = "main_running_data.json"

    # try:
    #     #for filename in os.listdir(data_folder):
    #         if filename.endswith(".json"):
    #             #file_path = os.path.join(DATA_FILE)
    #             with open(DATA_FILE, "r") as f:
    #                 try:
    #                     data = json.load(f)
    #                     combined_data.update(data)
    #                 except json.JSONDecodeError:
    #                     print(f"Warning: could not decode JSON in {filename}")
    # except Exception as e:
    #     print(f"Error reading data folder: {e}")
        
    # return combined_data

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
# ==============================
# ENCODING
# ==============================
def run_beacon_encoder():
    data = read_latest_json_data()
    # if not data:
    #     print("No sensor data available.")
    #     return None

    beacon_bytes = create_beacon(data)

    # Ensure it's bytes (convert if it's a string)
    if isinstance(beacon_bytes, str):
        beacon_bytes = bytes.fromhex(beacon_bytes)

    beacon_hex = beacon_bytes.hex().upper()
    print(f"Beacon Encoded (HEX):\n{beacon_hex}\n")

    with open("beacon_output.txt", "a") as f:
        f.write(beacon_hex + "\n")

    return beacon_bytes

if __name__ == "__main__":
    run_beacon_encoder()

# LoRa setup
CS = DigitalInOut(board.CE1) # init CS pin for SPI
RESET = DigitalInOut(board.D25) # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 436.95) # init object for the radio

# LoRa settings
# rfm9x.tx_power = 23 # TX power in dBm (23 dBm = 0.2 W)
# rfm9x.signal_bandwidtzh = 62500 # high bandwidth => high data rate and low range
# rfm9x.coding_rate = 6
# rfm9x.spreading_factor = 8
# rfm9x.enable_crc = True

print(rfm9x.tx_power)
print(rfm9x.signal_bandwidth)
print(rfm9x.coding_rate)
print(rfm9x.spreading_factor)

# Your transmissions will be in the form of a RAP packet. This is the flag for a beacon, as seen
#   in RAXRadioPacketFormat.pdf
BEACON_FLAG = 0x03

def send():
    # Keeping track of number of beacons sent
    count = 0
    UnixTime = hex(int(time.time()))
    beacon =  run_beacon_encoder()
    # Adding RAP packet wrapper
    rap = encode_rap(BEACON_FLAG, beacon)

    rap = encode_rap(BEACON_FLAG, beacon)  # returns bytes
    encoded = base64.b64encode(rap).decode("ascii")

    os.makedirs("transmission_data", exist_ok=True)

    with open("transmission_data/beacons", "a") as f:
        f.write(encoded + "\n")
    # Send packet
    #rfm9x.send(rap)
    print(count)
    count += 1

send()

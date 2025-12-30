import os
import smbus
import time
import sys
from ublox_gps import UbloxGps
from pyubx2 import UBXReader
import io
import read_helpers
from pynmeagps import NMEAReader
from smbus import SMBus
import logging_events_helper

bus = SMBus(1)

I2C_BUS = 1               
I2C_ADDR_GPS = 0x42       # Ublox NEO-M9N default I2C address

# UBX-CFG-PRT message (enable UBX+NMEA output on I2C)
cfg_prt = bytes([
    0xB5, 0x62,             # UBX header
    0x06, 0x00,             # CFG-PRT class and ID
    0x14, 0x00,             # length = 20
    0x01,                   # portID = 1 (I2C)
    0x00,                   # reserved
    0x00, 0x00, 0x00, 0x00, # txReady (not used)
    0x00, 0x00,             # mode (default)
    0x00, 0x00, 0x00, 0x00, # baudrate (not used)
    0x07, 0x00,             # inProtoMask: UBX + NMEA
    0x07, 0x00,             # outProtoMask: UBX + NMEA
    0x00, 0x00,             # flags
    0x00, 0x00              # reserved
])

# Calculate checksum
ck_a, ck_b = 0, 0
for b in cfg_prt[2:]:
    ck_a = (ck_a + b) & 0xFF
    ck_b = (ck_b + ck_a) & 0xFF
cfg_prt += bytes([ck_a, ck_b])

# Send it
bus.write_i2c_block_data(I2C_ADDR_GPS, 0xFF, list(cfg_prt[:32]))  # send first 32 bytes
if len(cfg_prt) > 32:
    bus.write_i2c_block_data(I2C_ADDR_GPS, 0xFF, list(cfg_prt[32:]))

def check_gps_lock():
    bus = smbus.SMBus(I2C_BUS)
    try:
        hi = bus.read_byte_data(I2C_ADDR_GPS, 0xFD)
        lo = bus.read_byte_data(I2C_ADDR_GPS, 0xFE)
        avail = (hi << 8) | lo
        # print(f"Available bytes: {avail}") 

        if avail == 0:
            print("No data available from GPS I2C stream.")
            return None

        to_read = min(avail, 100)
        data = []
        while to_read > 0:
            chunk = bus.read_i2c_block_data(I2C_ADDR_GPS, 0xFF, min(32, to_read))
            data.extend(chunk)
            to_read -= 32
            time.sleep(0.01)

        logging_events_helper.gps_lock_aquired_log()
        print(f"GPS raw data (first 16 bytes): {data[:16]}")

    except OSError as e:
        print("I2C error:", e)
        sys.exit(1)

if __name__ == "__main__":
    check_gps_lock()
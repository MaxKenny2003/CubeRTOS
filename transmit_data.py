import cv2
import numpy as np
import glob
from pathlib import Path
import base64
import json
import encode
import struct
import os
import math
import time
import busio
import board
import adafruit_rfm9x
from encode import encode_rap
from digitalio import DigitalInOut, Direction, Pull

CS = DigitalInOut(board.CE1) # init CS pin for SPI
RESET = DigitalInOut(board.D25) # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 436.95) # init object for the radio



def send_file(file_path, repeat_first=0):
    """Send lines from a file, optionally repeating the first line N times."""
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as f:
            lines = f.readlines()

        if not lines:
            return

        # Send first line multiple times if needed
        first_line = lines[0].strip()
        first_rap = base64.b64decode(first_line)
        for _ in range(repeat_first):
            rfm9x.send(first_rap)
            time.sleep(0.05)

        # Send remaining lines normally
        for line in lines:
            rap = base64.b64decode(line.strip())
            rfm9x.send(rap)
            time.sleep(0.05)

        # Truncate the file
        open(file_path, "w").close()


# Send main data, repeat first line 5x
send_file("transmission_data/data", repeat_first=5)

# Send beacons, no repetition
send_file("transmission_data/beacons")
import os
#import smbus
import time
import sys
#import adafruit_bme680
#import board
import json
import csv
from pathlib import Path
#from ublox_gps import UbloxGps
import write_helper

def main():
    # If you copy this file, files_to_read should be an array of file names that your read functions are writing to. 
    # newName is the name of prefix you want on all files related to the data. Then just call write_helper.write_data(files_to_read, newName)
    # The function should take care of literally everything else

    files_to_read = [
        "Eddy_data.json",
        "Packet_count.json",
        "BME680_data.json",
        "GPS_data.json",
        "IMU_data.json",
        "PiSystem_data.json",
        "Reboot_count.json",
        "TMP1_data.json",
        "TMP2_data.json"
    ]

    ### Debugging writing ### 
    # files_to_read = [
    #     "testFile.json"
    # ]

    newName = "sample_1_hz"
    
    write_helper.write_data(files_to_read, newName)


if __name__  == "__main__":
    main()
    

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

    files_to_read = [
        "RM3100_data.json"
    ]

    ### Debugging writing ### 
    # files_to_read = [
    #     "testFile2.json"
    # ]

    newName = "samples_10_hz"
    
    write_helper.write_data(files_to_read, newName)


if __name__  == "__main__":
    main()
    

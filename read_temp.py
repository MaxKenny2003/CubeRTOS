
import os
import smbus
import time
import sys
import json
import read_helpers
from ublox_gps import UbloxGps

def main():
    # with open(combined,'a') as f:
    #     pros_temp = os.popen('vcgencmd measure_temp').readline()     # read temperature
    #     print(pros_temp)
    #     mem = os.popen('free -h').read()          # Read memory 
    #     print(mem)
    #     storage = os.popen('df -h').read()        # Read used an free storage
    #     print(storage)

    i2c_ch = 1  # I2C bus number (usually 1 on newer Pis)
    i2c_address = 0x4B # TMP102 I2C address (default)
    bus = smbus.SMBus(1)
    reg_temp = 0x00

    try:
        # Example: read 4 bytes from register 0xFC
        temp_raw = bus.read_i2c_block_data(i2c_address, reg_temp, 2)
    except OSError as e:
        # OSError is raised for I2C errors (e.g. NACK, no device)
        print(f"Temp I2C error: {e}")
        sys.exit(1)

    # Process raw data into temperature (refer to TMP102 datasheet for conversion)
    temp = ((temp_raw[0] << 8) | temp_raw[1]) >> 4
    celsius = temp * 0.0625

    # Debug print statement
    #print(f"Temperature: {celsius:.2f}°C")

    dataDict = dict(tmp1 = celsius)
    read_helpers.write_to_json_temp_file(dataDict, "TMP1_data")
    
    sys.exit(0)

if __name__  == "__main__":
    main()
    
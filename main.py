import os
import smbus
import time
#import datetime as dt
#import matplotlib.pyplot as plt
from ublox_gps import UbloxGps


# Testing
def main():
    with open(combined,'a') as f:
        pros_temp = os.popen('vcgencmd measure_temp').readline()     # read temperature
        print(pros_temp)
        mem = os.popen('free -h').read()          # Read memory 
        print(mem)
        storage = os.popen('df -h').read()        # Read used an free storage
        print(storage)

    i2c_ch = 1  # I2C bus number (usually 1 on newer Pis)
    i2c_address = 0x4B # TMP102 I2C address (default)
    bus = smbus.SMBus(1)
    reg_temp = 0x00
    temp_raw = bus.read_i2c_block_data(i2c_address, reg_temp, 2)

    gps_port = smbus.SMBus(2)
    gps = UbloxGps(gps_port)
    
    i2c_address_gps = 0x42  #I2C address for the NEO M9N
    gps_data = bus.read_i2c_block_data(i2c_address_gps,0xFF)

    try:
        # Example: read 4 bytes from register 0xFC
        gps_data = bus.read_i2c_block_data(i2c_address_gps,0xFF)
    except OSError as e:
        # OSError is raised for I2C errors (e.g. NACK, no device)
        print(f"I2C error: {e}")

    # Process raw data into temperature (refer to TMP102 datasheet for conversion)
    temp = ((temp_raw[0] << 8) | temp_raw[1]) >> 4
    celsius = temp * 0.0625

    print(f"Temperature: {celsius:.2f}°C")
    print("GPS Data:")
    print(gps_data)

    with open(combined,'a') as f:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time)
        print(current_time, file=f)
        print(pros_temp)
        print(pros_temp, file=f)
        print(mem)
        print(mem, file=f)
        print(storage)
        print(storage, file=f)
        print(temp)
        print(temp, file=f)
        print(celsius)
        print(celsius, file=f)
        print('------------------------------------------------------') # separator
        print('------------------------------------------------------', file=f)

def log_reboot():
    LOG_FILE = '/home/alphacfl/logs/reboot_count.txt' 
    # If file exists, read current count
    if os.path.exists(LOG_FILE):
        with open('reboot_count.txt', "r") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                count = 0
    else:
        count = 0
    
    # Increment count
    count += 1

    # Write back updated count
    with open("reboot_count.txt", "w") as f:
        f.write(str(count))

    print(f"Reboot count: {count}")

if __name__  == "__main__":
     output_title = time.strftime("%Y-%m-%d %H:%M:%S")
     string2 = '.txt'
     combined = output_title + string2
     with open(combined,'w') as f:
         print('reboot', file=f)
    main()
import os
import read_helpers
import time
import sys

def read_reboot():
    LOG_FILE = '//home/alphacfl/logs/reboot_count_new.txt' 
    # If file exists, read current count
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                count = int(f.read().strip())
                dataDict = dict(num_resets=count)
                read_helpers.write_to_json_temp_file(dataDict, "Reboot_count")
                time.sleep(0.5)
            except OSError as e:
                print(f"I2C error: {e}")
                sys.exit(1)

if __name__ == "__main__":
    read_reboot()
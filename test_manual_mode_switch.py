"""This python test literally only exists to give a back door for mode switching"""
import os
import time
import json
import read_helpers
import sys

### Note ###
# if you use this, please do it with a large period (> 5s) as all it is going to do is forcibly insert a BME_altitude value into the main
# JSON file. 
# Also: Do not run any tasks that update the altitude or it will not work. This test is STRICTLY for manual mode switching

def main():
   ### See the comment above for necessary information on using this task
   # bme_altitude
    with open("main_running_data.json", "r") as f:
        main_data = json.load(f)

    key = "bme_altitude"
    if key in main_data:
        if(main_data[key] == 300):
            main_data[key] = 420          # modify existing value
        else:
            main_data[key] = 350          # modify existing value
    else:
        main_data[key] = 300          # add if missing

    with open("main_running_data.json", "w") as f:
        json.dump(main_data, f, indent=4)
    print(f"test_manual_mode_switch.py ran")


if __name__  == "__main__":
    main()

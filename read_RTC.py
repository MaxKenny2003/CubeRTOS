import qwiic_rv8803
import sys
import time
import read_helpers

# Changes need to be made...
# unix_time comes from the GPS time
# ranking of clocks
    # 1 is GPS time
    # 2 is RTC time
    # 3 is sys time
# strategy: every time a higher ranked time is recorded, sync the clocks below it

def main():

    try: 
        RTC = qwiic_rv8803.QwiicRV8803()
        time = RTC.update_time()
        dataDict = dict(rtc_time = time)
        read_helpers.write_to_json_temp_file(dataDict, "RTC_data")

        sys.exit(0)

    except OSError as e:
        # OSError is raised for I2C errors (e.g. NACK, no device)
        print(f"RTC I2C error: {e}")
        sys.exit(1)

if __name__  == "__main__":
    main()
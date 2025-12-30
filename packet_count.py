import os
import read_helpers
import time
import sys

# should probably add some logic to reset packet count to 0 when reboot occurs
# currently 0 is only set when we push to the pi or manually nano into packet_count.txt

def pack_count():
    LOG_FILE = '//home/alphacfl/Documents/packet_count.txt' 
    try:
        # If file exists, read current count
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                    count = int(f.read().strip())
        else:
            count = 0

        # Increment count
        count += 1
        # Write back updated count
        with open(LOG_FILE, "w") as f:
            f.write(str(count))

        dataDict = dict(packet_count=count)
        read_helpers.write_to_json_temp_file(dataDict, "Packet_count")
        print("------------------------ End of packet ", count, " ------------------------")
        time.sleep(0.05)

    except OSError as e:
                print(f"Error reading packet count: {e}")
                sys.exit(1)

if __name__ == "__main__":
    pack_count()
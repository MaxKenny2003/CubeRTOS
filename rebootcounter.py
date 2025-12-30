import os

def log_reboot():
    LOG_FILE = '//home/alphacfl/logs/reboot_count_new.txt' 
    # If file exists, read current count
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                count = int(f.read().strip())
            except ValueError:
                count = 0
    else:
        count = 0
    
    # Increment count
    count += 1

    # Write back updated count
    with open(LOG_FILE, "w") as f:
        f.write(str(count))

    print(f"Reboot count: {count}")

if __name__  == "__main__":
    
     log_reboot()
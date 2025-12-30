import os
import smbus
import time
import sys
import board
import json
import read_helpers


def main():
    try:
        # --- CPU Temperature ---
        pros_temp_output = os.popen('vcgencmd measure_temp').readline()
        # Format: temp=42.3'C
        format_temp = float(pros_temp_output.replace("temp=", "").replace("'C", "").strip())

        # --- Memory Info (kB) ---
        mem_output = os.popen('free -k').read().splitlines()
        mem_values = mem_output[1].split()
        used_mem = mem_values[2]          # in kB
        format_used_mem = int(used_mem)
        free_mem = mem_values[3]          # in kB
        format_free_mem = int(free_mem)

        # --- Disk Info (kB) ---
        disk_output = os.popen('df -k /').read().splitlines()
        disk_values = disk_output[1].split()
        used_disk = disk_values[2]        # in kB
        format_used_disk = int(used_disk)
        free_disk = disk_values[3]        # in kB
        format_free_disk = int(free_disk)

        # --- CPU Load (% actual usage) ---
        def read_cpu_times():
            with open('/proc/stat') as f:
                fields = f.readline().split()[1:8]
                return list(map(int, fields))

        cpu1 = read_cpu_times()
        time.sleep(1.0)
        cpu2 = read_cpu_times()

        idle1 = cpu1[3] + cpu1[4]
        idle2 = cpu2[3] + cpu2[4]

        total1 = sum(cpu1)
        total2 = sum(cpu2)

        total_diff = total2 - total1
        idle_diff = idle2 - idle1

        cpu_usage_percent = round(100 * (1 - idle_diff / total_diff), 2)
        load_avg = cpu_usage_percent

        # --- Organize data ---
        dataDict = dict(
            cpu_temp=format_temp,                # Celsius
            cpu_load=load_avg,                   # %
            used_memory=format_used_mem,         # kB
            free_memory=format_free_mem,         # kB
            used_disk=format_used_disk,          # kB
            free_disk=format_free_disk           # kB
        )

        # Debug Print
        # print(f"Used Memory: {format_used_mem} kB")
        # print(f"Free Memory: {format_free_mem} kB")
        # print(f"Used Disk Space: {format_used_disk} kB")
        # print(f"Free Disk Space: {format_free_disk} kB")
        # print(f"CPU Load: {load_avg} %")
        # print(f"CPU Temp: {format_temp} Celsius")

        # Write to JSON
        read_helpers.write_to_json_temp_file(dataDict, "PiSystem_data")

        sys.exit(0)

    except OSError as e:
        print(f"Pi I2C error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

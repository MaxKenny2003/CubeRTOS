import serial
import time
import sys

UART_PORT = "/dev/ttyS0"
BAUD_RATE = 9600

def check_gps_lock():
    try:
        ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=0.5)
        print(f"Opened UART on {UART_PORT} at {BAUD_RATE} baud")
    except serial.SerialException as e:
        print(f"Failed to open UART: {e}")
        sys.exit(1)

    start = time.time()

    while time.time() - start < 5:
        line = ser.readline().decode(errors='ignore').strip()
        if not line:
            continue

        if line.startswith("$G"):
            print(line)

            # $GNGGA,...,fixQuality,...
            if line.startswith("$GNGGA") or line.startswith("$GPGGA"):
                parts = line.split(",")
                if len(parts) > 6:
                    fix_quality = parts[6]
                    if fix_quality in ["1", "2"]:  # 1=GPS fix, 2=DGPS fix
                        print("GPS has lock")
                        ser.close()
                        sys.exit(0)
                    else:
                        print("No GPS lock yet")

    print("No GPS lock within 5s.")
    ser.close()
    sys.exit(1)

if __name__ == "__main__":
    check_gps_lock()
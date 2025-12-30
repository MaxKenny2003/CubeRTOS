import serial
import time
import sys
import io
from pynmeagps import NMEAReader
from pyubx2 import UBXReader
import read_helpers

# UART port & baud rate
UART_PORT = "/dev/ttyS0"   # or "/dev/serial0" depending on your setup
BAUD_RATE = 9600

def main():
    try:
        # Open serial connection
        ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=0.1)
        #print(f"Opened UART on {UART_PORT} at {BAUD_RATE} baud")
    except serial.SerialException as e:
        print(f"Failed to open UART: {e}")
        sys.exit(1)

    buffer = bytearray()
    start = time.time()

    while time.time() - start < 5:
        try:
            # Read any available data
            data = ser.read(1024)
            if not data:
                time.sleep(0.01)
                continue
            buffer.extend(data)

            # --- Parse NMEA frames ---
            while True:
                ds = buffer.find(b'$')
                if ds == -1:
                    break
                de = buffer.find(b'\r\n', ds)
                if de == -1:
                    break
                line = buffer[ds:de]
                buffer = buffer[de + 2:]
                try:
                    msg = NMEAReader.parse(line.decode('ascii', 'ignore'))
                    if msg and msg.msgID in ('GGA', 'RMC'):
                        lat = getattr(msg, 'lat', None)
                        lon = getattr(msg, 'lon', None)
                        alt = getattr(msg, 'alt', None)
                        vel = getattr(msg, 'vel', None)
                        print(f'NMEA {msg.msgID} lat={lat} lon={lon} alt={alt} vel={vel}')
                except Exception:
                    pass

            # --- Parse UBX frames (NAV-PVT, etc.) ---
            while True:
                idx = buffer.find(b'\xb5\x62')
                if idx == -1:
                    break
                if idx > 0:
                    del buffer[:idx]
                ubr = UBXReader(io.BytesIO(buffer), quitonerror=False)
                raw, parsed = ubr.read()
                if not raw:
                    break  # incomplete frame
                del buffer[:len(raw)]  # consume parsed frame
                if parsed and getattr(parsed, 'identity', '') == "NAV-PVT":
                    dataDict = {
                        "unix_time": parsed.iTOW,
                        "gps_lat": parsed.lat / 1e7,
                        "gps_lon": parsed.lon / 1e7,
                        "gps_alt": parsed.hMSL / 1000,
                        "gps_velocity": parsed.gSpeed / 1000,
                        "gps_num_sats": parsed.numSV,
                    }
                    print(dataDict)
                    read_helpers.write_to_json_temp_file(dataDict, "GPS_data")
                    ser.close()
                    sys.exit(0)

            # keep buffer small
            if len(buffer) > 4096:
                buffer = buffer[-4096:]

        except serial.SerialException as e:
            print("UART read error:", e)
            ser.close()
            sys.exit(1)

    print("No GPS data available within 5s")
    ser.close()
    sys.exit(0) # GPS is retried for data every run of scheduler


if __name__ == "__main__":
    main()
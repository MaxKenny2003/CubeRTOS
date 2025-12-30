import os
import time
import sys
import errno
import subprocess
from smbus import SMBus
from pynmeagps import NMEAReader
import read_helpers

I2C_BUS = 1
I2C_ADDR_GPS = 0x42  # u-blox NEO-M9N default I2C address

# u-blox I2C registers used
REG_AVAIL_H = 0xFD
REG_AVAIL_L = 0xFE
REG_DATA = 0xFF

# config
INITIAL_DRAIN_SEC = 0.2
MAIN_LOOP_TIMEOUT = 5.0
MAX_I2C_ERRORS = 6
SAFE_BLOCK_MAX = 16


def read_avail(bus):
    hi = bus.read_byte_data(I2C_ADDR_GPS, REG_AVAIL_H)
    lo = bus.read_byte_data(I2C_ADDR_GPS, REG_AVAIL_L)
    return (hi << 8) | lo


def safe_read_chunk(bus, want):
    if want <= 0:
        return b''
    try:
        chunk = bus.read_i2c_block_data(I2C_ADDR_GPS, REG_DATA, want)
        return bytes(chunk)
    except OSError as e:
        if getattr(e, "errno", None) not in (errno.EIO, errno.EREMOTEIO, 121, None):
            raise
        out = bytearray()
        for _ in range(want):
            try:
                b = bus.read_byte_data(I2C_ADDR_GPS, REG_DATA)
                out.append(b)
            except OSError:
                break
        return bytes(out)


def main():
    bus = SMBus(I2C_BUS)
    buffer = bytearray()

    # This holds the latest values
    last = {
        "lat": None,
        "lon": None,
        "alt": None,
        "vel": None,
        "numSV": None
    }

    # Flags: Require **both** GGA and RMC before writing JSON
    have_gga = False
    have_rmc = False

    # Initial quick drain to align to NMEA boundaries
    t0 = time.time()
    while time.time() - t0 < INITIAL_DRAIN_SEC:
        try:
            avail = read_avail(bus)
            if avail:
                to_read = min(avail, SAFE_BLOCK_MAX)
                safe_read_chunk(bus, to_read)
            else:
                time.sleep(0.01)
        except OSError:
            break

    start = time.time()
    i2c_errors = 0

    while time.time() - start < MAIN_LOOP_TIMEOUT:
        try:
            avail = read_avail(bus)
            if avail == 0:
                time.sleep(0.01)
                i2c_errors = 0
                continue

            to_read = min(avail, SAFE_BLOCK_MAX)
            chunk = safe_read_chunk(bus, to_read)

            if not chunk:
                i2c_errors += 1
                if i2c_errors >= MAX_I2C_ERRORS:
                    print("Too many consecutive I2C read failures; exiting.")
                    sys.exit(1)
                time.sleep(0.05)
                continue
            else:
                i2c_errors = 0

            buffer.extend(chunk)

            # Parse complete NMEA lines
            while True:
                ds = buffer.find(b'$')
                if ds == -1:
                    if len(buffer) > 1024:
                        buffer = buffer[-1024:]
                    break

                de = buffer.find(b'\r\n', ds)
                if de == -1:
                    if ds > 0:
                        del buffer[:ds]
                    break

                line = bytes(buffer[ds:de])
                print("RAW NMEA:", line.decode("ascii", "ignore"))

                del buffer[:de + 2]

                try:
                    msg = NMEAReader.parse(line.decode("ascii", "ignore"))
                    if not msg:
                        continue

                    mid = getattr(msg, 'msgID', '')

                    # lat/lon appear in both GGA and RMC
                    if hasattr(msg, 'lat') and msg.lat is not None:
                        last['lat'] = msg.lat
                    if hasattr(msg, 'lon') and msg.lon is not None:
                        last['lon'] = msg.lon

                    # ----- GGA -----
                    if mid == 'GGA':
                        have_gga = True

                        alt = getattr(msg, 'alt', None)
                        try:
                            last['alt'] = int(float(alt))
                        except Exception:
                            last['alt'] = None

                        numsv = getattr(msg, 'numSV', None)
                        try:
                            last['numSV'] = int(numsv)
                        except Exception:
                            last['numSV'] = None

                    # ----- RMC -----
                    if mid == 'RMC':
                        have_rmc = True

                        spd_kn = getattr(msg, 'spd', None)
                        try:
                            spd_kn = float(spd_kn)
                            last['vel'] = spd_kn * 0.514444
                        except Exception:
                            last['vel'] = None

                    print(f"NMEA {mid} lat={last['lat']} lon={last['lon']} alt={last['alt']} vel={last['vel']} numSV={last['numSV']}")

                    # ---------------------------------------------------------
                    # Exit only when we have BOTH RMC + GGA + valid lat/lon
                    # ---------------------------------------------------------
                    if have_gga and have_rmc and last['lat'] is not None and last['lon'] is not None:

                        # No None in JSON
                        for key in ("alt", "vel", "numSV"):
                            if last[key] is None:
                                last[key] = 0

                        unix_time = int(time.time())
                        dataDict = {
                            "unix_time": unix_time,
                            "gps_lat": last['lat'],
                            "gps_lon": last['lon'],
                            "gps_alt": last['alt'],
                            "gps_velocity": last['vel'],
                            "gps_num_sats": last['numSV'],
                        }

                        read_helpers.write_to_json_temp_file(dataDict, "GPS_data")

                        try:
                            subprocess.run(["sudo", "date", "-s", f"@{unix_time}"], check=False)
                        except Exception as e:
                            print("Failed to sync time:", e)

                        print("✔ Combined GGA + RMC written to beacon.")
                        sys.exit(0)

                except Exception:
                    continue

            # keep buffer size safe
            if len(buffer) > 4096:
                buffer = buffer[-4096:]

        except OSError as e:
            print("GPS I2C error:", e)
            i2c_errors += 1
            if i2c_errors >= MAX_I2C_ERRORS:
                sys.exit(1)
            time.sleep(0.05)

    print("No GPS data within timeout.")
    sys.exit(0)


if __name__ == "__main__":
    main()
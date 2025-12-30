import smbus
import time
import sys
import read_helpers

RM3100_ADDR = 0x20
I2C_BUS = 1

CMM = 0x01
TMRC = 0x0B
MX = 0x24
STATUS = 0x34
POLLCMD = 0x00

bus = smbus.SMBus(I2C_BUS)

def write_reg(reg, val):
    bus.write_byte_data(RM3100_ADDR, reg, val)

def read_regs(start_reg, length):
    return bus.read_i2c_block_data(RM3100_ADDR, start_reg, length)

def twos_comp(val, bits):
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val

def read_field():
    data = read_regs(MX, 9)
    x = twos_comp((data[0] << 16) | (data[1] << 8) | data[2], 24)
    y = twos_comp((data[3] << 16) | (data[4] << 8) | data[5], 24)
    z = twos_comp((data[6] << 16) | (data[7] << 8) | data[8], 24)
    return x, y, z

def setup_rm3100():
    # Cycle count = 200 for X, Y, Z
    bus.write_i2c_block_data(RM3100_ADDR, 0x04, [0x00, 0xC8])
    bus.write_i2c_block_data(RM3100_ADDR, 0x06, [0x00, 0xC8])
    bus.write_i2c_block_data(RM3100_ADDR, 0x08, [0x00, 0xC8])

    # Set TMRC = 0x95 → 20 Hz sample rate
    write_reg(TMRC, 0x95)

    # Start continuous measurement on X, Y, Z
    write_reg(CMM, 0x77) # enable XYZ in continuous mode
    time.sleep(0.1)

    print("RM3100 setup complete!")

def counts_to_uT(val, cycle_count=200):
    return val / (75 * (cycle_count / 200))


# DEBUG -------------------------------
# ADDR = 0x21
# bus = smbus.SMBus(1)

# def wr(r, v): bus.write_byte_data(ADDR, r, v)
def rd(r, n): return bus.read_i2c_block_data(RM3100_ADDR, r, n)

# print("Checking status...")
# print("Status:", hex(rd(0x34, 1)[0]))

# print("Setting up...")
# bus.write_i2c_block_data(ADDR, 0x04, [0x00,0xC8,0x00,0xC8,0x00,0xC8])
# wr(0x0B, 0x92)
# wr(0x01, 0x70)
# time.sleep(0.5)

#print("Status after setup:", hex(rd(0x34, 1)[0]))
#print("Raw data:", rd(0x24, 9))
#print("Who am I:", hex(bus.read_byte_data(0x21, 0x36)))
#DEBUG ---------------------

def main():
    try:
        setup_rm3100()
        #print("Status after setup:", hex(rd(0x34, 1)[0]))
        time.sleep(0.005)

        # DEBUGGING ----------------------
        #write_reg(0x04, 0x00)  # X high byte
        #write_reg(0x05, 0xC8)  # X low byte = 200
        #print("X cycle count readback:", read_regs(0x04,2))
        # END OF DEBUGGING --------------------

        # Wait for data ready
        #status = read_regs(STATUS, 1)[0]
        #print("RM3100 read_regs() complete!", status)
        t0 = time.time()
        timeout = 1.0  # seconds
        while True:
            status = read_regs(STATUS, 1)[0]
            # bits 0..2 are DRDY for X,Y,Z respectively
            if (status & 0x80):
                break
            if (time.time() - t0) > timeout:
                print(f"Timeout waiting for DRDY, status=0x{status:02X}")
                return
            time.sleep(0.005)

        # New: store raw counts for transmission; print uT for humans
        x_counts, y_counts, z_counts = read_field()
        x_uT = counts_to_uT(x_counts)  # cycle_count defaults to 200
        y_uT = counts_to_uT(y_counts)
        z_uT = counts_to_uT(z_counts)
        print(f"Magnetic Field (uT): X={x_uT:.2f}, Y={y_uT:.2f}, Z={z_uT:.2f}")
        dataDict = dict(
            rm3100_mag_x=int(x_counts),
            rm3100_mag_y=int(y_counts),
            rm3100_mag_z=int(z_counts),
            rm3100_cycle_count=200,
        )
        read_helpers.write_to_json_temp_file(dataDict, "RM3100_data")

    except OSError as e:
        print(f"RM3100 I2C error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

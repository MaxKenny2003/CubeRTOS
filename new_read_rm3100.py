import smbus
import time
import sys
import read_helpers

# Change this if i2cdetect shows 0x23 instead of 0x20
RM3100_ADDR = 0x32 
I2C_BUS = 1

# Register addresses (from RM3100 datasheet)
CMM = 0x01           # Continuous measurement mode control
TMRC = 0x0B          # Cycle count registers
MX = 0x24            # X axis result MSB
STATUS = 0x34        # Status register
POLLCMD = 0x00       # Poll command register

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
    # Each axis is 3 bytes (24 bits)
    data = read_regs(MX, 9)
    x = twos_comp((data[0] << 16) | (data[1] << 8) | data[2], 24)
    y = twos_comp((data[3] << 16) | (data[4] << 8) | data[5], 24)
    z = twos_comp((data[6] << 16) | (data[7] << 8) | data[8], 24)
    return x, y, z

def setup_rm3100():
    # Example config: 200 Hz measurement rate (per datasheet)
    write_reg(TMRC, 0x92)
    # Put in continuous measurement mode (XYZ)
    write_reg(CMM, 0x70)
    time.sleep(0.1)

def poll_measurement():
    # Trigger a measurement in poll mode
    write_reg(POLLCMD, 0x70)
    # Wait until data ready bit is set
    while True:
        status = read_regs(STATUS, 1)[0]
        if status & 0x80:  # DRDY bit
            break
        time.sleep(0.01)
    return read_field()

def main():
    try:
        setup_rm3100()
        mag_x, mag_y, mag_z = poll_measurement()
        print(f"Magnetic field (uT): X={mag_x:.2f}, Y={mag_y:.2f}, Z={mag_z:.2f}")
        # Add a delay if needed to control reading frequency
        dataDict = dict(rm3100_mag_x = mag_x, rm3100_mag_y = mag_y, rm3100_mag_z = mag_z)
        time.sleep(0.1)
    except OSError as e:
        # OSError is raised for I2C errors (e.g. NACK, no device)
        print(f"I2C error: {e}")
        sys.exit(1) 

    read_helpers.write_to_json_temp_file(dataDict, "RM3100_data")

    sys.exit(0)

if __name__ == "__main__":
    main()
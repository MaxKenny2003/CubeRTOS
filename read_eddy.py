import smbus
import sys
import time
import math
import read_helpers

# I2C setup
ADS7828_ADDRESS = 0x4B  # Eddy PDU ADC I2C address
bus = smbus.SMBus(1)
VREF = 3.3  # ADC reference voltage

# Channel command bytes from your mapping
CHANNEL_COMMANDS = {
    "V_3V3": 0x84,
    "V_5V0": 0xC4,
    "V_BATT": 0x94,
    "I_3V3": 0xD4,
    "I_5V0": 0xA4,
    "I_BATT": 0xE4,
    "TEMP_3V3": 0xB4,
    "TEMP_5V0": 0xF4
}

# Divider ratios for voltage scaling
DIVIDER_RATIOS = {
    "3V3": 1.0,                # direct measurement
    "5V0": 3.3 / 5.0,          # voltage divider scaling (adjust if known)
    "BATT": 6.8 / (22 + 6.8)   # typical for 6.8k/(22k+6.8k)
}

# Current sense resistor and amplifier gain
CURRENT_SENSE = {
    "3V3": dict(shunt_ohm=0.1, amp_gain=20),
    "5V0": dict(shunt_ohm=0.1, amp_gain=20),
    "BATT": dict(shunt_ohm=0.1, amp_gain=20)
}

# Thermistor parameters for regulator temps
TEMP_SENSOR = {
    "3V3": dict(beta=3950, nominal_res=10000, nominal_temp=25),
    "5V0": dict(beta=3950, nominal_res=10000, nominal_temp=25)
}

def read_ads7828_channel(cmd):
    bus.write_byte(ADS7828_ADDRESS, cmd)
    high = bus.read_byte(ADS7828_ADDRESS)
    low = bus.read_byte(ADS7828_ADDRESS)
    raw = ((high & 0x0F) << 8) | low
    voltage = (raw / 4095.0) * VREF
    return raw, voltage

def read_voltage(label):
    rail = label.split('_')[1]
    raw, v_meas = read_ads7828_channel(CHANNEL_COMMANDS[label])
    v_actual = v_meas / DIVIDER_RATIOS[rail]
    return v_actual

def read_current(label):
    rail = label.split('_')[1]
    raw, v_sense = read_ads7828_channel(CHANNEL_COMMANDS[label])
    shunt = CURRENT_SENSE[rail]['shunt_ohm']
    gain = CURRENT_SENSE[rail]['amp_gain']
    current = v_sense / (shunt * gain)
    return current

def read_temperature(label):
    rail = label.split('_')[1]
    raw, v = read_ads7828_channel(CHANNEL_COMMANDS[label])
    R_therm = 10000 * (VREF / v - 1)  # assuming 10k pull-up to 3.3V
    beta = TEMP_SENSOR[rail]['beta']
    R0 = TEMP_SENSOR[rail]['nominal_res']
    T0 = TEMP_SENSOR[rail]['nominal_temp'] + 273.15
    tempK = 1 / ((1 / T0) + (1 / beta) * math.log(R_therm / R0))
    return tempK - 273.15

def main():
    try:
        dataDict = dict(
            v_3v3 = read_voltage("V_3V3"),
            i_3v3 = read_current("I_3V3"),
            v_5v0 = read_voltage("V_5V0"),
            i_5v0 = read_current("I_5V0"),
            v_batt = read_voltage("V_BATT"),
            i_batt = read_current("I_BATT"),
            temp_3v3 = read_temperature("TEMP_3V3"),
            temp_5v0 = read_temperature("TEMP_5V0")
        )

    except OSError as e:
        print(f"Eddy I2C error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    read_helpers.write_to_json_temp_file(dataDict, "Eddy_data")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
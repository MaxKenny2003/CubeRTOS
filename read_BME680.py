import os
import smbus
import time
import sys
import adafruit_bme680
import board
import json
import read_helpers
from ublox_gps import UbloxGps


def main():
    i2c = board.I2C()
    sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)   # attach the sensor to where it is on the board
    sensor.seaLevelhPa = 1014.5                         # Set the sea level

    # Printing for debugging
    #print('Temperature: {} degrees C'.format(sensor.temperature))
    #print('Gas: {} ohms'.format(sensor.gas))
    #print('Humidity: {}%'.format(sensor.humidity))
    #print('Pressure: {}hPa'.format(sensor.pressure))
    #print('Altitude: {} meters'.format(sensor.altitude))

    try:
        dataDict = dict(bme_temp = sensor.temperature, bme_humidity = sensor.humidity, bme_pressure = sensor.pressure, bme_altitude = sensor.altitude)
    except OSError as e:
        print("BME680 I2C error:", e)
        sys.exit(1)

    read_helpers.write_to_json_temp_file(dataDict, "BME680_data")

    sys.exit(0)



if __name__  == "__main__":
    main()
    
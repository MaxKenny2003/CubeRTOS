import os
import smbus
import time
import sys
import qwiic_icm20948
import board
import json
import read_helpers
from ublox_gps import UbloxGps


def main():

    try:
        IMU = qwiic_icm20948.QwiicIcm20948()

        IMU = qwiic_icm20948.QwiicIcm20948()

        IMU.begin()

        if IMU.dataReady():
            IMU.getAgmt() # read all axis and temp from sensor, note this also updates all instance variables
            # print(\
            #     '{: 06d}'.format(IMU.axRaw)\
            # , '\t', '{: 06d}'.format(IMU.ayRaw)\
            # , '\t', '{: 06d}'.format(IMU.azRaw)\
            # , '\t', '{: 06d}'.format(IMU.gxRaw)\
            # , '\t', '{: 06d}'.format(IMU.gyRaw)\
            # , '\t', '{: 06d}'.format(IMU.gzRaw)\
            # , '\t', '{: 06d}'.format(IMU.mxRaw)\
            # , '\t', '{: 06d}'.format(IMU.myRaw)\
            # , '\t', '{: 06d}'.format(IMU.mzRaw)\
            # )
            dataDict = dict(accel_x = IMU.axRaw, accel_y = IMU.ayRaw, accel_z = IMU.azRaw, gyro_x = IMU.gxRaw, gyro_y = IMU.gyRaw, gyro_z = IMU.gzRaw, mag_x = IMU.mxRaw, mag_y = IMU.myRaw, mag_z = IMU.mzRaw)
            
    except OSError as e:
        # OSError is raised for I2C errors (e.g. NACK, no device)
        print(f"IMU I2C error: {e}")
        sys.exit(1) 

    read_helpers.write_to_json_temp_file(dataDict, "IMU_data")

    sys.exit(0)


if __name__  == "__main__":
    main()
    
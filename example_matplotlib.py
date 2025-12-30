import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import adafruit_bme680
import qwiic_ccs811

# Create figure for plotting
fig = plt.figure()
# Subplot for BME280 temperature
ax1 = fig.add_subplot(331)
xs = []
ys1 = []
# Subplot for BME280 humidity
ax2 = fig.add_subplot(332)
ys2 = []
# Subplot for BME280 pressure
ax3 = fig.add_subplot(333)
ys3 = []
# Subplot for CCS811 equivalent CO2
ax4 = fig.add_subplot(334)
ys4 = []
# Subplot for CCS811 total volatile organic compounds (TVOC)
ax5 = fig.add_subplot(335)
ys5 = []
# Initialize communication with BME280
BME280 =  adafruit_bme680.Adafruit_BME680_I2C(0x77)
if BME280.connected == False:
    print("The Qwiic BME680 isn't connected to the system. Please check connection")
    BME280.begin()

# Initialize communication with CCS811
CCS811 = qwiic_ccs811.QwiicCcs811()
if CCS811.connected == False:
    print("The Qwiic CCS811 isn't connected to the system. Please check connection")
    CCS811.begin()

# This function is called periodically from FuncAnimation
def animate(i):
    # Read temperature from BME280
    temperature = round(BME280.temperature_fahrenheit, 2)
    # Read humidity from BME280
    humidity = round(BME280.humidity, 2)
    # Read pressure from BME280
    pressure = round(BME280.pressure, 2)
    # Read equivalent CO2 from CCS811
    CCS811.read_algorithm_results()
    cO2 = round(CCS811.CO2, 2)
    # Read TVOC from CCS811
    tVOC = round(CCS811.TVOC, 2)
    # Add values to list
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys1.append(temperature)
    ys2.append(humidity)
    ys3.append(pressure)
    ys4.append(cO2)
    ys5.append(tVOC)
    # Plot environmental temperature
    ax1.clear()
    ax1.plot(xs, ys1)
    ax1.set_xlabel('%H:%M:%S.%f')
    ax1.set_ylabel('Temperature (degrees F)')
    ax1.set_title('BME280 Temperature over Time')
    # Plot environmental humidity
    ax2.clear()
    ax2.plot(xs, ys2)
    ax2.set_xlabel('%H:%M:%S.%f')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_title('BME280 Humidity over Time')
    # Plot environmental pressure

    ax3.clear()
    ax3.plot(xs, ys3)
    ax3.set_xlabel('%H:%M:%S.%f')
    ax3.set_ylabel('Pressure (Pa)')
    ax3.set_title('BME280 Pressure over Time')
    # Plot environmental equivalent CO2
    ax4.clear()
    ax4.plot(xs, ys4)
    ax4.set_xlabel('%H:%M:%S.%f')
    ax4.set_ylabel('Equivalent CO2 (PPm)')
    ax4.set_title('CCS811 Equivalent CO2 over Time')
    # Plot environmental TVOC
    ax5.clear()
    ax5.plot(xs, ys5)
    ax5.set_xlabel('%H:%M:%S.%f')
    ax5.set_ylabel('TVOC (PPb)')
    ax5.set_title('CCS811 TVOC over Time')
    # Plot subplots
    ax1 = plt.subplot(331)
    ax2 = plt.subplot(332)
    ax3 = plt.subplot(333)
    ax4 = plt.subplot(334)
    ax5 = plt.subplot(335)
    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()
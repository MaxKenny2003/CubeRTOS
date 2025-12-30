import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)

print("Pin 17 HIGH. Measure voltage.")
while True:
    time.sleep(1)
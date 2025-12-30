import RPi.GPIO as GPIO
import time
import sys

# Define the GPIO pin connected to the LED
LED_PIN = 17  # You can change this to your chosen GPIO pin

def main():
    try:
        # Set the GPIO mode (BCM refers to Broadcom chip-specific pin numbers)
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        # Set the chosen pin as an output
        GPIO.setup(LED_PIN, GPIO.OUT)
        # Turn the LED on (HIGH)
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        sys.exit(0)

    except OSError as e:
            print("Flight LED not working:", e)
            sys.exit(1)

if __name__ == "__main__":
    main()
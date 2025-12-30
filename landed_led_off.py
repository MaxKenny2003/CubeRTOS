import RPi.GPIO as GPIO
import time
import sys

# Define the GPIO pin connected to the LED
LED_PIN = 18  # You can change this to your chosen GPIO pin

def main():
    try:
        # Set the GPIO mode (BCM refers to Broadcom chip-specific pin numbers)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Set the chosen pin as an output
        GPIO.setup(LED_PIN, GPIO.OUT)
        # Turn the LED off (LOW)
        GPIO.output(LED_PIN, GPIO.LOW)
        # Clean up GPIO settings to reset pins to default state
        GPIO.cleanup()
        sys.exit(0)

    except OSError as e:
            print("Flight LED not working:", e)
            sys.exit(1)

if __name__ == "__main__":
    main()
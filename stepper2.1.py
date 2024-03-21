import time
import RPi.GPIO as GPIO
import random

# Define Constants
DIR = 21
STEP = 20
CW = 1
CCW = 0
SPR = 3200
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_ROTATION = 60  # Maximum rotation limit in degrees
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

def rotate(steps, direction, delay):
    GPIO.output(DIR, direction)
    for _ in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

def return_to_origin():
    step_count = int(SPR * MAX_ROTATION / DEGREES_PER_REV)  # Calculate step count for 60 degrees rotation
    delay = 0.0001

    rotate(step_count, CCW, delay)  # Rotate counterclockwise to return to origin

def main():
    directions = [CW, CCW]  # List of directions

    for _ in range(5):
        direction = random.choice(directions)  # Choose a random direction
        rotate(MAX_ROTATION, direction, 0.0001)  # Rotate a maximum of 60 degrees
        time.sleep(2)
        return_to_origin()  # Return to origin

if __name__ == "__main__":
    main()

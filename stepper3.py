import time
import RPi.GPIO as GPIO

# Constants
DIR = 21  # Direction GPIO Pin
STEP = 20  # Step GPIO Pin
CW = 1  # Clockwise Rotation
CCW = 0  # Counter Clockwise Rotation
SPR = 3200  # Steps per Revolution
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_DEGREES = 60  # Max degrees from origin
GPIO.setwarnings(False)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

delay = 0.0001  # Delay between each step

def rotate_motor(degrees, direction):
    if abs(degrees) > MAX_DEGREES:
        # Limit rotation to MAX_DEGREES
        degrees = MAX_DEGREES if degrees > 0 else -MAX_DEGREES
    
    steps = int(abs(degrees) / DEGREES_PER_STEP)  # Calculate the number of steps
    GPIO.output(DIR, CW if direction == 'cw' else CCW)
    
    for _ in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

# Example usage
try:
    rotate_motor(60, 'cw')  # Rotate 60 degrees clockwise
    time.sleep(2)  # Wait for 2 seconds
    rotate_motor(60, 'ccw')  # Rotate 60 degrees counter-clockwise to return to original position
finally:
    print("hello")
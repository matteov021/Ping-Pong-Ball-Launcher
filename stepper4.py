import time
import RPi.GPIO as GPIO
import random

# Constants
DIR = 21
STEP = 20
CW = 1
CCW = 0
SPR = 3200
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_DEGREES = 60
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

def rotate_motor(degrees, direction, speed):
    
    steps = int(abs(degrees) / DEGREES_PER_STEP)  # Calculate the number of steps
    GPIO.output(DIR, CW if direction == 'cw' else CCW)
    
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)

# TODO: Def For DC motors that takes in speed % (PWM), maybe enable

# Generate 6 random rotations and execute them with random speeds
for _ in range(6):
    
    degrees = random.randint(-MAX_DEGREES, MAX_DEGREES)
    direction = 'cw' if degrees > 0 else 'ccw'
    speed = random.uniform(0.0001, 0.001)
    
    print(f"Rotating {degrees} degrees {direction} with speed {speed:.4f}")
    rotate_motor(degrees, direction, speed)
    time.sleep(2)
    
    # LOGIC HAS TO BE IN HERE TO CHANGE DC MOTOR such that after turning, it waits 2 seconds, ramps up the motor to a random
    # duty cycle, holds for 5 seconds at that speed, then it slows down to 0 before continuing the program
    # The DC motors must be at 0 speed before it returnes to origin

    # Return To Origin
    rotate_motor(degrees, 'ccw' if direction == 'cw' else 'cw', speed)
    print(f"Returning to origin from {degrees} degrees {direction} with speed {speed:.4f}")
    time.sleep(2)
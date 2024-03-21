import time
import RPi.GPIO as GPIO

DIR = 21
STEP = 20
CW = 1
CCW = 0
SPR = 3200  # Steps per revolution
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR

def move_stepper_motor(movements):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)

    delay = 0.0001

    # Calculate step counts for each movement
    step_counts = [int(degrees / DEGREES_PER_STEP) for degrees, _ in movements]

    # Move according to the defined movements
    for movement in movements:
        degrees, direction = movement
        step_count = int(degrees / DEGREES_PER_STEP)

        # Perform the movement
        for _ in range(step_count):
            GPIO.output(DIR, direction)
            GPIO.output(STEP, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(STEP, GPIO.LOW)
            time.sleep(delay)

        time.sleep(2)  # Pause between movements

    # Return to origin state
    total_forward_steps = sum(step_counts)
    total_backward_steps = SPR - total_forward_steps  # Calculate backward steps
    for _ in range(total_backward_steps):
        GPIO.output(DIR, not CW)  # Reverse the direction
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

    time.sleep(2)  # Pause between movements

# Example usage:
movements = [(30, CW), (70, CCW), (50, CW), (80, CCW)]
move_stepper_motor(movements)

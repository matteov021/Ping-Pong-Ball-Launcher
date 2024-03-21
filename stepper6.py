import time
import RPi.GPIO as GPIO
import random

# Constants
GPIO.setwarnings(False)
DIR = 21
STEP = 20
PWM_PIN = 16
CW = 1
CCW = 0
SPR = 3200
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_DEGREES = 90

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)

dc_motor_pwm = GPIO.PWM(PWM_PIN, 1000)  # PWM frequency 1000 Hz
dc_motor_pwm.start(0)                   # Start with 0% duty cycle

def map_value_to_degrees(value):
    # Maps value from 0-600 range to -90 to +90 degrees
    return (value - 300) / ((600 - 0) / (MAX_DEGREES - (-MAX_DEGREES)))  # (600 - 0) / (90 - (-90)) = 4

def rotate_stepper_motor(degrees, direction, speed):
    steps = int(abs(degrees) / DEGREES_PER_STEP)  # Calculate the number of steps
    GPIO.output(DIR, CW if direction == 'cw' else CCW)
    
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)

def control_dc_motor(duty_cycle):
    dc_motor_pwm.ChangeDutyCycle(duty_cycle)    # Set duty cycle
    time.sleep(2)                               # Hold for 5 seconds
    dc_motor_pwm.ChangeDutyCycle(0)             # Slow down to 0

# Generate 6 random rotations and execute them with random speeds
for _ in range(6):
    value = random.randint(0, 600)  # Random value between 0 and 600
    degrees = map_value_to_degrees(value)
    direction = 'cww' if degrees > 0 else 'cw'
    speed = random.uniform(0.0001, 0.001)
    duty_cycle = random.randint(5, 15)
    
    # Control Motor Direction
    print(f"Rotating to {degrees} degrees {direction} with speed {speed:.4f}")
    print(f"Rotating to {value}")
    rotate_stepper_motor(degrees, direction, speed)
    time.sleep(1)

    # Control DC Motor
    print(f"Controlling DC motor with duty cycle: {duty_cycle}%")
    control_dc_motor(duty_cycle)
    time.sleep(1)

    # Return To Origin
    rotate_stepper_motor(degrees, 'ccw' if direction == 'cw' else 'cw', speed)
    print(f"Returning to origin from {degrees} degrees {direction} with speed {speed:.4f}\n")
    time.sleep(1)

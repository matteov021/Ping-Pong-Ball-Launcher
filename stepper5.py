import time
import RPi.GPIO as GPIO
import random

# Constants
GPIO.setwarnings(False)
DIR = 21
STEP = 20
CW = 1
CCW = 0
SPR = 3200
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_DEGREES = 60
PWM_PIN = 16 # Temp

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)

dc_motor_pwm = GPIO.PWM(PWM_PIN, 1000)  # PWM frequency 1000 Hz
dc_motor_pwm.start(0)                   # Start with 0% duty cycle

def rotate_stepper_motor(degrees, direction, speed):
    
    steps = int(abs(degrees) / DEGREES_PER_STEP)  # Calculate the number of steps
    GPIO.output(DIR, CW if direction == 'cw' else CCW)
    
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)

def control_dc_motor(duty_cycle):
    
    time.sleep(2)                               # Wait for 2 seconds
    dc_motor_pwm.ChangeDutyCycle(duty_cycle)    # Set duty cycle
    time.sleep(5)                               # Hold for 5 seconds
    dc_motor_pwm.ChangeDutyCycle(0)             # Slow down to 0
    time.sleep(2)                               # Wait for 2 seconds

# Generate 6 random rotations and execute them with random speeds
for _ in range(6):
    
    degrees = random.randint(-MAX_DEGREES, MAX_DEGREES)
    direction = 'cw' if degrees > 0 else 'ccw'
    speed = random.uniform(0.0001, 0.001)
    duty_cycle = random.randint(5, 30)
    
    # Control Motor Direction
    print(f"Rotating {degrees} degrees {direction} with speed {speed:.4f}")
    rotate_stepper_motor(degrees, direction, speed)
    time.sleep(2)

    # Control DC Motor
    print(f"Controlling DC motor with duty cycle: {duty_cycle}%")
    control_dc_motor(duty_cycle)
    time.sleep(2)

    # Return To Origin
    rotate_stepper_motor(degrees, 'ccw' if direction == 'cw' else 'cw', speed)
    print(f"Returning to origin from {degrees} degrees {direction} with speed {speed:.4f}")
    time.sleep(2)
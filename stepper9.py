import time
import RPi.GPIO as GPIO
import random

# Constants
GPIO.setwarnings(False)
DIR = 13
STEP = 6
PWM_PIN = 12
PWM_PIN2 = 27
SOLENOID_PIN = 23
CW = 1
CCW = 0
SPR = 3200
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_DEGREES = 30

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
#GPIO.setup(PWM_PIN2, GPIO.OUT)
GPIO.setup(SOLENOID_PIN, GPIO.OUT)

dc_motor_pwm = GPIO.PWM(PWM_PIN, 490)    # PWM frequency 1000 Hz
#dc_motor_pwm2 = GPIO.PWM(PWM_PIN2, 490)  # PWM frequency 1000 Hz
dc_motor_pwm.start(0)                     # Start with 0% duty cycle
#dc_motor_pwm2.start(0)                    # Start with 0% duty cycle

def map_value_to_degrees(value):
    return (value - 300) / ((600 - 0) / (MAX_DEGREES - (-MAX_DEGREES))) # Maps value from 0-600 range to -90 to +90 degrees

def rotate_stepper_motor(degrees, direction, speed):
    steps = int(abs(degrees) / DEGREES_PER_STEP)  # Calculate the number of steps
    GPIO.output(DIR, CW if direction == 'cw' else CCW)
    
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)
        f.write(f"{x}\n{direction}\n")  

def control_dc_motor(duty_cycle):
    dc_motor_pwm.ChangeDutyCycle(duty_cycle)    # Set duty cycle
    # dc_motor_pwm2.ChangeDutyCycle(duty_cycle)   # Set duty cycle
    time.sleep(1)                               # Hold for 2 seconds

def pulse_solenoid():
    GPIO.output(SOLENOID_PIN, GPIO.LOW)   # Deactivate solenoid
    time.sleep(0.1)                       # Keep activated for 0.5 seconds
    GPIO.output(SOLENOID_PIN, GPIO.HIGH)  # Deactivate solenoid

def return_to_origin_if_exit():
    with open("/home/pi/Desktop/ENEL400/StepMotorBackup.txt", "r") as f:
        lines = f.read().splitlines()
        last_direction = lines[-1]
        last_step = lines[-2]

    GPIO.output(DIR, CCW if last_direction == 'cw' else CW)
    origin_fix = int(last_step)

    for x in range(origin_fix):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(0.001)

    with open("/home/pi/Desktop/ENEL400/StepMotorBackup.txt", "w") as f:
        f.write("")

# Initialize motor position by returning to origin
f = open("/home/pi/Desktop/ENEL400/StepMotorBackup.txt", "r") 
if (f.read() != ''):
    f.close()
    return_to_origin_if_exit()
else:
    f.close()

f = open("/home/pi/Desktop/ENEL400/StepMotorBackup.txt", "w")

try:
    for x in range(6):
        #value = random.randint(0, 600)              # Random value between 0 and 600
        value = 300
        degrees = map_value_to_degrees(value)
        direction = 'ccw' if degrees > 0 else 'cw'
        # speed = random.uniform(0.0005, 0.001)
        speed = 0.0005
        duty_cycle = random.randint(80, 81)
        
        # Control DC Motor
        print(f"Controlling DC motor with duty cycle: {duty_cycle}%")
        control_dc_motor(duty_cycle)
       
        # Control Motor Direction
        print(f"Rotating to {degrees} degrees {direction} with speed {speed:.4f}")
        print(f"Rotating to {value}")
        rotate_stepper_motor(degrees, direction, speed)
        # time.sleep(1)
        pulse_solenoid()                            # Pulse Solenoid
        print("Pulsing Solenoid")
        # dc_motor_pwm.ChangeDutyCycle(0)             # Slow down to 0
        # dc_motor_pwm2.ChangeDutyCycle(0)            # Slow down to 0
        # time.sleep(2)

        # Return To Origin
        rotate_stepper_motor(degrees, 'ccw' if direction == 'cw' else 'cw', speed)
        print(f"Returning to origin from {degrees} degrees {direction} with speed {speed:.4f}\n")
        f.write("0\ncw\n")
        print("Origin Reached")
        # time.sleep(2)

finally:
    f.close()
import time
import RPi.GPIO as GPIO
import random
import cv2
from picamera2 import Picamera2
import mediapipe as mp

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
MAX_DEGREES = 20

# Button setup (Can Be Modified)
SPEED_UP_BTN = 2
SPEED_DOWN_BTN = 3
DUTY_CYCLE_UP_BTN = 14
DUTY_CYCLE_DOWN_BTN = 15
START_BTN = 4

speed = 0.00075  # Initial speed
duty_cycle = 15  # Initial duty cycle

# Setup MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Constants and GPIO setup code remains unchanged

# Initialize PiCamera2
piCam = Picamera2()
piCam.preview_configuration.main.size=(1280,720)
piCam.preview_configuration.main.format="RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

GPIO.setmode(GPIO.BCM)
GPIO.setup([DIR, STEP, PWM_PIN, PWM_PIN2, SOLENOID_PIN], GPIO.OUT)
GPIO.setup([SPEED_UP_BTN, SPEED_DOWN_BTN, DUTY_CYCLE_UP_BTN, DUTY_CYCLE_DOWN_BTN, START_BTN], GPIO.IN, pull_up_down = GPIO.PUD_UP)

dc_motor_pwm = GPIO.PWM(PWM_PIN, 490)    # PWM frequency 1000 Hz
dc_motor_pwm.start(0)                    # Start with 0% duty cycle

def get_face_position():
    frame = piCam.capture_array()
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_image)
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y = int(bboxC.xmin * iw), int(bboxC.ymin * ih)
            w, h = int(bboxC.width * iw), int(bboxC.height * ih)
            return x + w // 2
    else:
        return None

def map_value_to_degrees(value):
    return (value - 600) / ((1200 - 0) / (MAX_DEGREES - (-MAX_DEGREES))) # Maps value from 0-1200 range to -90 to +90 degrees

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
    time.sleep(2)                               # Hold for 2 seconds

def adjust_speed(increase = True):
    global speed
    if increase:
        speed = min(speed + 0.0001, 0.001)
        print(f"Speed Increased {speed}")
    else:
        speed = max(speed - 0.0001, 0.0005)
        print(f"Speed Decreased {speed}")

def adjust_duty_cycle(increase = True):
    global duty_cycle
    if increase:
        duty_cycle = min(duty_cycle + 1, 25)
        print(f"Duty Increase {duty_cycle}")
    else:
        duty_cycle = max(duty_cycle - 1, 5)
        print(f"Duty Decreased {duty_cycle}")

def pulse_solenoid():
    GPIO.output(SOLENOID_PIN, GPIO.LOW)  # Activate solenoid
    time.sleep(0.1)                      # Keep activated for 0.5 seconds
    GPIO.output(SOLENOID_PIN, GPIO.HIGH) # Deactivate solenoid

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

def run_program():
    global speed, duty_cycle
    face_detected_count = 0  # Initialize counter for detected faces

    while face_detected_count < 30:  # Keep running until 30 faces have been processed

        if not GPIO.input(START_BTN):
            break;
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Break loop if 'q' is pressed
            break

        if random.choice([True, False]):
            value = get_face_position()
            print("Processing face position...")
        else:
            # value = get_hand_position()
            print("Processing hand position...")


        if value is not None:
            degrees = map_value_to_degrees(value)
            direction = 'ccw' if degrees > 0 else 'cw'
            
            # Control DC Motor with the global duty_cycle variable
            print(f"Controlling DC motor with duty cycle: {duty_cycle}%")
            control_dc_motor(duty_cycle)
        
            # Control Motor Direction using the global speed variable
            print(f"Rotating to {degrees} degrees {direction} with speed {speed:.4f}")
            rotate_stepper_motor(degrees, direction, speed)
            time.sleep(1)
            pulse_solenoid()  # Pulse Solenoid
            dc_motor_pwm.ChangeDutyCycle(0)  # Stop DC motor
            time.sleep(2)

            # Return To Origin
            rotate_stepper_motor(degrees, 'ccw' if direction == 'cw' else 'cw', speed)
            print(f"Returning to origin from {degrees} degrees {direction} with speed {speed:.4f}")
            f.write("0\ncw")
            print("Origin Reached")
            time.sleep(2)

            face_detected_count += 1  # Increment the face detected counter

        else:
            # If no face is detected, you might want to add a short delay here
            # to prevent the program from running too fast and overwhelming the CPU
            time.sleep(0.1)

# Initialize motor position by returning to origin
f = open("/home/pi/Desktop/ENEL400/StepMotorBackup.txt", "r") 
if (f.read() != ''):
    f.close()
    return_to_origin_if_exit()
else:
    f.close()

f = open("/home/pi/Desktop/ENEL400/StepMotorBackup.txt", "w")

try:
    while True:
        # Check button states
        if not GPIO.input(SPEED_UP_BTN):
            adjust_speed(increase = True)
            time.sleep(1)
        if not GPIO.input(SPEED_DOWN_BTN):
            adjust_speed(increase = False)
            time.sleep(1)
        if not GPIO.input(DUTY_CYCLE_UP_BTN):
            adjust_duty_cycle(increase = True)
            time.sleep(1)
        if not GPIO.input(DUTY_CYCLE_DOWN_BTN):
            adjust_duty_cycle(increase = False)
            time.sleep(1)
        if not GPIO.input(START_BTN):
            time.sleep(5)
            run_program()
            print("Completed 30 cycles of face detection and processing.")
        time.sleep(0.1)
finally:
    f.close()
    piCam.stop()
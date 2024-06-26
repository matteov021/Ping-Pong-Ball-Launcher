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
SOLENOID_PIN = 5
CW = 1
CCW = 0
SPR = 3200
DEGREES_PER_REV = 360
DEGREES_PER_STEP = DEGREES_PER_REV / SPR
MAX_DEGREES = 25

# Button setup (Can Be Modified)
SPEED_UP_BTN = 2
SPEED_DOWN_BTN = 3
DUTY_CYCLE_UP_BTN = 14
DUTY_CYCLE_DOWN_BTN = 15
START_BTN = 4

speed = 0.0008   # Initial speed
wait_time = 0.8 # Inital Wait Time
duty_cycle = 15  # Initial duty cycle

# Setup MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Constants and GPIO setup code remains unchanged

# Initialize PiCamera2
piCam = Picamera2()
piCam.preview_configuration.main.size=(720,480)
piCam.preview_configuration.main.format="RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

GPIO.setmode(GPIO.BCM)
GPIO.setup([DIR, STEP, PWM_PIN, PWM_PIN2], GPIO.OUT)
GPIO.setup(SOLENOID_PIN, GPIO.OUT, initial = GPIO.HIGH)
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

def get_hand_position():
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hand_detection:
        frame = piCam.capture_array()
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hand_detection.process(rgb_image)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                x, y = int(wrist.x * 760), int(wrist.y * 400)
                print(x)
                return x # POSSIBLE FIXXXXXXXXXXXXXXXXXXXXX
        else:
            return None

def map_value_to_degrees(value):
    return (value - 350) / ((700 - 0) / (MAX_DEGREES - (-MAX_DEGREES))) # Maps value from 0-1200 range to -90 to +90 degrees

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
    # time.sleep(2)                             # Hold for 2 seconds

def adjust_speed(increase = True):  
    global speed
    global wait_time
    if increase:
        speed = min(speed + 0.0001, 0.001)
        wait_time = min(wait_time + 0.1, 1)
        print(f"Speed Increased {speed}")
        print(f"Wait Increased {wait_time}")
    else:
        speed = max(speed - 0.0001, 0.0005)
        wait_time = max(wait_time - 0.1, 0.5)
        print(f"Speed Decreased {speed}")
        print(f"Wait Decreased {wait_time}")

def adjust_duty_cycle(increase = True):
    global duty_cycle
    if increase:
        duty_cycle = min(duty_cycle + 1, 30)
        print(f"Duty Increase {duty_cycle}")
    else:
        duty_cycle = max(duty_cycle - 1, 5)
        print(f"Duty Decreased {duty_cycle}")

def pulse_solenoid():
    GPIO.output(SOLENOID_PIN, GPIO.LOW)  # Activate solenoid
    time.sleep(0.01)                      # Keep activated for 0.5 seconds
    GPIO.output(SOLENOID_PIN, GPIO.HIGH) # Deactivate solenoid

def run_program():
    global speed, duty_cycle
    face_detected_count = 0  # Initialize counter for detected faces

    while face_detected_count < 10:  # Keep running until 30 faces have been processed

        if not GPIO.input(START_BTN):
            break;
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Break loop if 'q' is pressed
            break

        choices = ['face'] * 5 + ['hand'] * 5
        action = random.choice(choices)

        if (action == 'face'):
            value = get_face_position()
            print("Processing face position...")
        elif (action == 'hand'):
            value = get_hand_position()
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
            # time.sleep(1)
            # time.sleep(0.1)
            pulse_solenoid()  # Pulse Solenoid
            # dc_motor_pwm.ChangeDutyCycle(0)  # Stop DC motor
            # time.sleep(2)

            # Return To Origin
            rotate_stepper_motor(degrees, 'ccw' if direction == 'cw' else 'cw', speed)
            print(f"Returning to origin from {degrees} degrees {direction} with speed {speed:.4f}")
            print("Origin Reached")
            time.sleep(wait_time)

            face_detected_count += 1  # Increment the face detected counter

        else:
            # If no face is detected, you might want to add a short delay here
            # to prevent the program from running too fast and overwhelming the CPU
            time.sleep(0.1)

try:
    while True:
        # Check button states
        if not GPIO.input(SPEED_DOWN_BTN):
            adjust_speed(increase = True)
            time.sleep(0.5)
        if not GPIO.input(SPEED_UP_BTN):
            adjust_speed(increase = False)
            time.sleep(0.5)
        if not GPIO.input(DUTY_CYCLE_UP_BTN):
            adjust_duty_cycle(increase = True)
            time.sleep(0.5)
        if not GPIO.input(DUTY_CYCLE_DOWN_BTN):
            adjust_duty_cycle(increase = False)
            time.sleep(0.5)
        if not GPIO.input(START_BTN):
            
            start_time = time.time()
            button_held = True  # Assume the button will be held down

            while time.time() - start_time < 2:  # Check for 3 seconds
                if GPIO.input(START_BTN):  # If button is released
                    button_held = False
                    break  # Exit the while loop if button is released
                time.sleep(0.1)  # Short delay to prevent high CPU usage

            if button_held:
                time.sleep(3)
                control_dc_motor(duty_cycle)
                time.sleep(2)
                run_program()
                print("Completed 10 cycles of face detection and processing.")
                dc_motor_pwm.ChangeDutyCycle(0)  # Stop DC motor
        time.sleep(0.1)
        # GPIO.output(SOLENOID_PIN, GPIO.HIGH) # Deactivate solenoid

finally:
    piCam.stop()
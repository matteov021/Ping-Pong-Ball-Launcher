import cv2
import mediapipe as mp
import time
from picamera2 import Picamera2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

piCam = Picamera2()
preview_config = piCam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
piCam.configure(preview_config)
piCam.start()

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hand_detection:
    while True:
        frame = piCam.capture_array()
        # Ensure the image is in RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_image = cv2.flip(rgb_image, 1)
        results = hand_detection.process(rgb_image)
        
        # Convert back to BGR for OpenCV displaying
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    bgr_image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                )
        
        cv2.imshow('Hand Detection', bgr_image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
piCam.stop()
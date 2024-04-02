import cv2
import mediapipe as mp
import time
from picamera2 import Picamera2

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

piCam = Picamera2()
preview_config = piCam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
piCam.configure(preview_config)
piCam.start()

with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
    while True:
        frame = piCam.capture_array()
        # Ensure the image is in RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_image = cv2.flip(rgb_image, 1)
        results = face_detection.process(rgb_image)
        
        # Convert back to BGR for OpenCV displaying
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(bgr_image, detection)
        
        cv2.imshow('Face Detection', bgr_image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
piCam.stop()
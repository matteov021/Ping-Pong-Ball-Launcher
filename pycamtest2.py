# face_detection_module.py
import cv2
from picamera2 import Picamera2

piCam = Picamera2()
piCam.preview_configuration.main.size = (640, 480)
piCam.preview_configuration.main.format = "RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def get_face_position():

    frame = piCam.capture_array()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    piCam.stop()  # Stop the camera

    if len(faces) > 0:
        x, y, w, h = faces[0]  # Use the first detected face
        return x + w // 2      # Return the X coordinate of the face's center
    else:
        return None

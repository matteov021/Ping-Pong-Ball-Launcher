import cv2
import mediapipe as mp

# Initialize MediaPipe Face Detection.
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam.
cap = cv2.VideoCapture(0)

with mp_face_detection.FaceDetection(
    min_detection_confidence=0.5) as face_detection:
    while cap.isOpened():
        # Read a frame from the webcam.
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Convert the image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # Process the image with MediaPipe Face Detection.
        results = face_detection.process(image)

        # Draw face detection annotations on the image if faces are detected.
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(image, detection)
                
                # Extract bounding box coordinates of the detected face.
                bbox_coords = detection.location_data.relative_bounding_box
                image_height, image_width, _ = image.shape
                xmin = int(bbox_coords.xmin * image_width)
                ymin = int(bbox_coords.ymin * image_height)
                xmax = int((bbox_coords.xmin + bbox_coords.width) * image_width)
                ymax = int((bbox_coords.ymin + bbox_coords.height) * image_height)
                
                # Print the coordinates when 'r' key is pressed.
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    print("Face Bounding Box Coordinates:", ((xmin+xmax)/2, (ymin+ymax)/2))

        # Display the image with face detection annotations.
        cv2.imshow('Face Detection', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Press 'q' to exit.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the webcam and close all OpenCV windows.
cap.release()
cv2.destroyAllWindows()

import cv2
import mediapipe as mp

# Initialize MediaPipe Hands.
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam.
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        # Read a frame from the webcam.
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Convert the image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # Process the image with MediaPipe Hands.
        results = hands.process(image)

        # Draw hand landmarks on the image if hands are detected.
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on the image.
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Extract coordinates of hand landmarks.
                landmark_coords = []
                for landmark in hand_landmarks.landmark:
                    landmark_x = landmark.x * image.shape[1]
                    landmark_y = landmark.y * image.shape[0]
                    landmark_coords.append((landmark_x, landmark_y))

                # Print or use the coordinates when 'r' key is pressed.
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    print("Hand Landmark Coordinates:", landmark_coords[-1])

        # Display the image with hand landmarks.
        cv2.imshow('Hand Landmarks', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Press 'q' to exit.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the webcam and close all OpenCV windows.
cap.release()
cv2.destroyAllWindows()

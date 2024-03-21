import cv2
from picamera2 import Picamera2

piCam = Picamera2()
piCam.preview_configuration.main.size=(640,480)
piCam.preview_configuration.main.format="RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

'''
while True:
    frame = piCam.capture_array()
    cv2.imshow("piCam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
'''

# Load pre-trained Haar cascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Initialize list to store positional data
positional_data = []

f = open("StepMotorTest.txt", "w")

while True:
    # Capture frame-by-frame
    frame = piCam.capture_array()
    
    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Record positional data of faces
    for (x, y, w, h) in faces:
        # Add the coordinates of the center of the bounding box
        # The coordinates given are in [x,y] axis, 2 dimensional
        if cv2.waitKey(1) & 0xFF == ord('r'):
            positional_data.append((x + w//2, y + h//2))
            print("Positional data:", positional_data[-1])
            
            # Write the position data to the file
            f.write(str(positional_data[-1][0])) #Only retrieving x coordinates
            f.write("\n")
            f.close()

            # Read the position data from the file
            f = open("StepMotorTest.txt", "r")
            lines = f.read().splitlines()
            last_line = lines[-1]
            print("The positional data " + last_line)
            f.close()
            
            # Set up to write to file without erasing existing data
            f = open("StepMotorTest.txt", "a")
        # Draw bounding box around detected faces
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Display the resulting frame
    cv2.imshow('piCam', frame)
    
    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cv2.destroyAllWindows()
f.close()

# Print positional data

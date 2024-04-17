import cv2
import supervision as sv
from qreader import QReader
from ultralytics import YOLO

# Create a QReader instance
qreader = QReader()

# Load the model
model = YOLO('./models/n1280/weights/best.pt') 
# model = YOLO('yolov8n.pt')

# Create a VideoCapture object
cam = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cam.isOpened():
    print("Error: Could not open camera.")
    exit()

# Capture loop
while True:
    # Capture frame-by-frame
    ret, frame = cam.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Error: Failed to grab frame")
        break
    
    results = model.predict(frame, conf=0.7, verbose=False)
    
    if len(results[0]) > 0:
        first_detection = results[0][0]
        
        # put 'results' to annotate all detections instead
        detections = sv.Detections.from_ultralytics(first_detection) 
        
        labels = [
            model.model.names[class_id]
            for class_id
            in detections.class_id
        ]

        annotated_image = sv.BoundingBoxAnnotator().annotate(scene=frame, detections=detections)
        annotated_image = sv.LabelAnnotator().annotate(scene=annotated_image, detections=detections, labels=labels)

        # Extract the first detection region of interest
        x_min, y_min, x_max, y_max = detections.xyxy[0]
        detect_region = frame[int(y_min):int(y_max), int(x_min):int(x_max)];

        # Use the qreader to detect and decode the QR code
        decoded_text = qreader.detect_and_decode(image=detect_region)

        print(decoded_text)

        cv2.imshow('detections', detect_region)
        cv2.imshow('annotations', annotated_image)

    else:
        cv2.imshow('annotations', frame)    
        cv2.imshow('detections', (0, 0, 0))

    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cam.release()
cv2.destroyAllWindows()

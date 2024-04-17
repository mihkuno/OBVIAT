from qreader import QReader
import cv2

# Create a QReader instance
qreader = QReader()

# Open the default webcam (you can change the index if you have multiple webcams)
video_capture = cv2.VideoCapture(0)

# Check if the webcam is opened successfully
if not video_capture.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Read a frame from the webcam
    ret, frame = video_capture.read()

    # Convert the frame to RGB format (QReader expects RGB images)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Use the detect_and_decode function to get the decoded QR data
    decoded_text = qreader.detect_and_decode(image=rgb_frame)

    # Print the decoded text (you can modify this part based on your needs)
    if decoded_text:
        print("Decoded QR Code:", decoded_text)

    # Display the frame with the QR code (optional)
    cv2.imshow("QR Code Scanner", frame)

    # Break the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the OpenCV window
video_capture.release()
cv2.destroyAllWindows()
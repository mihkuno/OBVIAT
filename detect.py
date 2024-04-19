import os
import cv2
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import supervision as sv
from qreader import QReader
from ultralytics import YOLO

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


#  Configs
# ==============================================

output_folder      = 'output'
camera_index       = 0 # for built-in camera, 1 or 2 for external camera
weights_path       = './models/n1280/weights/best.pt'
smtp_username      = "..." # sender email
smtp_password      = "..." # sender password
receiver_email     = "..." # recipient email
subject            = "Student Attendance Report: " # system includes the current time
body               = "Good day, here is the attached csv file for the report."
time_of_report     = "17:00"      # report at 5pm 
pause_duration     = 14 * 60 * 60 # pause for 14 hours

# ==============================================

# Creating Global DataFrame
attendance = {
    'Name': [],
    'Grade': [],
    'Section': [],
    'LRN': [],
    'Time': []
}

def handleDecodedText(decoded_text):
    global attendance

    try:
        # spilt the decoded text    
        grade_section   = decoded_text.split('\n')[1]
        student_name    = decoded_text.split('\n')[0]
        student_grade   = grade_section.split('-')[0].strip()
        student_section = grade_section.split('-')[1][1:].strip()
        student_lrn     = decoded_text.split('\n')[2]
        current_time    = datetime.now().strftime('%H:%M:%S')

        # Append the data to the global DataFrame if not exist
        if student_lrn not in attendance['LRN']:
            attendance['Name'].append(student_name)
            attendance['Grade'].append(student_grade)
            attendance['Section'].append(student_section)
            attendance['LRN'].append(student_lrn)
            attendance['Time'].append(current_time)
            
        print('The attendance in memory is: ', attendance)
    
    except Exception as e:
        print(decoded_text)
        print("QR code is not in the specified format.")


def handleScheduledReport():
    global output_folder
    global body
    global subject
    global attendance
    global smtp_username
    global smtp_password
    global receiver_email
    global time_of_report
    global pause_duration

    # create dataframe
    df = pd.DataFrame(attendance)
    
    # create output folder if not exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Generating file name with current date and time
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'student_data_{current_time}.csv'
    file_path = os.path.join(output_folder, file_name)

    # Export to CSV
    df.to_csv(file_path, index=False)

    print(f"File saved to: {file_path}")

    # clear the attendance object
    attendance = {
        'Name': [],
        'Grade': [],
        'Section': [],
        'LRN': [],
        'Attendance': []
    }
    
    # Gmail SMTP server configuration
    sender_email  = smtp_username
    smtp_server   = "smtp.gmail.com"
    smtp_port     = 587

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject + current_time # add current time to the subject

    # Attach body to the email
    message.attach(MIMEText(body, "plain"))

    # Attach CSV file
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file_name}",
    )
    message.attach(part)

    # Connect to Gmail's SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(smtp_username, smtp_password)  # Login to your Gmail account

    # Send email
    server.sendmail(sender_email, receiver_email, message.as_string())

    # Quit SMTP server
    server.quit()

    print("Email has been sent successfully!")        
    
        
# Create a QReader instance
qreader = QReader()

# Load the model
model = YOLO(weights_path) 

# Create a VideoCapture object
cam = cv2.VideoCapture(camera_index)

# Check if the camera is opened successfully
if not cam.isOpened():
    print("Error: Could not open camera.")
    exit()

# Capture loop
while True:
    
    # if time is 5pm, save the output file then email it
    if datetime.now().strftime('%H:%M') == time_of_report:
        print(f'It is now {time_of_report}, generating student attendance report..')
        handleScheduledReport()
            
        # pause for 14 hours (5pm (17) to 7am = 14 hours)
        print('\nPausing the program..')
        cv2.destroyAllWindows()
        time.sleep(pause_duration)
        print('\nResuming the program..')        
    
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

        # Extract the first roi detection
        x_min, y_min, x_max, y_max = detections.xyxy[0]
        detect_region = frame[int(y_min):int(y_max), int(x_min):int(x_max)];

        # Use the qreader to detect and decode the QR code
        decoded_text = qreader.detect_and_decode(image=detect_region)

        if decoded_text:
            # Extract the first qr detection
            decoded_text = decoded_text[0] 
            if decoded_text is not None:
                handleDecodedText(decoded_text)

        cv2.imshow('detections', detect_region)
        cv2.imshow('annotations', annotated_image)

    else:
        black_image = np.zeros((0, 0, 3), dtype=np.uint8)
        cv2.imshow('annotations', frame)    
        cv2.imshow('detections', black_image)

    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cam.release()
cv2.destroyAllWindows()

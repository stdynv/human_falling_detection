import cv2
import sys
from ultralytics import YOLO
import pandas as pd
import cvzone
from collections import deque
import time
import mediapipe as mp
import torch
import warnings
import random
import requests
import logging
import os

warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')

# Configure PyTorch to use CPU globally
torch.device('cpu')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load YOLOv8 Nano model
model = YOLO("yolov8n.pt")
logging.getLogger('ultralytics').setLevel(logging.ERROR)

# Initialize class list from coco.txt
with open("coco.txt", "r") as file:
    class_list = file.read().split("\n")

# Initialize Mediapipe for pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture from webcam
cap = cv2.VideoCapture(0)

# Define parameters for recording sequences
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec for better compatibility

# File to keep frames before the fall (5 seconds before)
buffer_length = int(5 * fps)
pre_frames = deque(maxlen=buffer_length)

# Variables for post-fall recording
post_recording = False
post_count = 0
post_length = int(5 * fps)  # 5 seconds after the fall

# Counter for optimizing frame processing
count = 0

# Variables for tracking position and size
previous_positions = deque(maxlen=5)

# Fall counter and room number
fall_count = 0
room_number = 49

# Cooldown to avoid multiple detections
cooldown_time = 5
last_fall_time = 0

# API URL for uploading videos and incident reporting
upload_url = "https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/api/azure/upload"  # Replace with your Flask API URL
incident_url = 'https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/api/incidents/create'


while True:
    ret, frame = cap.read()
    count += 1

    # Skip every other frame for processing speed
    if count % 2 != 0:
        continue

    if not ret:
        break

    frame = cv2.resize(frame, (1020, 600))
    frame_for_recording = frame.copy()

    # Record frames before fall detection
    if not post_recording:
        pre_frames.append(frame_for_recording.copy())

    sys.stdout = open(os.devnull, 'w')
    # Make predictions with YOLOv8 Nano
    results = model(frame)

    if len(results[0].boxes) == 0:
        cv2.putText(frame, 'No Detection', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("RGB", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue
    
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    person_count = sum(1 for index, row in px.iterrows() if class_list[int(row[5])] == 'person')

    bed_couch_boxes = []

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])

        c = class_list[int(row[5])]
        confidence = row[4]
        if confidence < 0.5:
            continue

        cvzone.putTextRect(frame, f'{c} {confidence:.2f}', (x1, y1), 1, 1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if 'person' in c:
            h = y2 - y1
            w = x2 - x1
            aspect_ratio = h / w
            area = h * w
            
            cvzone.putTextRect(frame, f'Aspect Ratio: {aspect_ratio:.2f}', (x1, y1 - 30), 1, 1, colorR=(255, 255, 0))
            
            current_position = (x1 + x2) // 2, y2
            previous_positions.append(current_position)

            if area > 100000:
                cvzone.putTextRect(frame, "Person too close, ignoring fall", (x1, y1 - 60), 1, 1, colorR=(0, 0, 255))
                continue

            on_bed_or_couch = False
            for bx1, by1, bx2, by2 in bed_couch_boxes:
                if x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1:
                    on_bed_or_couch = True
                    break

            if on_bed_or_couch:
                cvzone.putTextRect(frame, "Person on bed/couch, ignoring fall", (x1, y1 - 60), 1, 1, colorR=(0, 0, 255))
                continue

            person_frame = frame[y1:y2, x1:x2]
            person_rgb = cv2.cvtColor(person_frame, cv2.COLOR_BGR2RGB)
            results_pose = pose.process(person_rgb)

            if results_pose.pose_landmarks:
                mp_drawing.draw_landmarks(
                    person_frame, 
                    results_pose.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

            frame[y1:y2, x1:x2] = person_frame

            if aspect_ratio < 1.2:
                vertical_speeds = [previous_positions[i][1] - previous_positions[i - 1][1] for i in range(1, len(previous_positions))]
                avg_speed = sum(vertical_speeds) / len(vertical_speeds) if vertical_speeds else 0

                cvzone.putTextRect(frame, f'Speed: {avg_speed:.2f}', (x1, y1 - 60), 1, 1, colorR=(0, 255, 255))

                current_time = time.time()
                if avg_speed > 10 and (current_time - last_fall_time) > cooldown_time:
                    fall_count += 1
                    room_number = random.randint(1, 100)
                    fall_time = time.strftime("%Y-%m-%d %H:%M:%S")

                    last_fall_time = current_time

                    cvzone.putTextRect(frame, f'Fall Detected! Count: {fall_count}, Room: {room_number}', (x1, y1 - 90), 1, 1, colorR=(255, 0, 0))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    file_name = f'chute_detectee_{time.strftime("%Y%m%d-%H%M%S")}_room_{room_number}'
                    video_file_name = f'{file_name}.mp4'

                    if not post_recording:
                        out = cv2.VideoWriter(video_file_name, fourcc, fps, (frame.shape[1], frame.shape[0]))

                        for f in pre_frames:
                            out.write(f)

                        post_recording = True
                        post_count = 0

    info_text = f'People: {person_count} | Falls: {fall_count} | Room: {room_number}'
    cvzone.putTextRect(frame, info_text, (10, 10), scale=1.5, thickness=2, colorT=(0, 0, 0), colorR=(200, 200, 200, 120), offset=10)

    if post_recording:
        out.write(frame_for_recording)
        post_count += 1
        if post_count >= post_length:
            post_recording = False
            out.release()

            # Upload the video to Azure Blob Storage via the Flask API
            headers = {
                'Content-Type': 'multipart/form-data'
            }
            
            if os.path.exists(video_file_name):
                try:
                    # Open the file in binary mode
                    with open(video_file_name, 'rb') as video_file:
                        files = {'video': (video_file_name, video_file, 'video/mp4')}
                        
                        # Make the POST request to upload the file
                        response = requests.post(upload_url, files=files)

                        # Check the response for the SAS URL of the uploaded video
                        if response.status_code == 200:
                            logging.info("Video uploaded successfully.")
                            logging.info("SAS URL: %s", response.json().get("sas_url"))
                            sas_url = response.json().get("sas_url")

                            # Prepare the JSON data to be sent to the incidents API
                            incident_data = {
                                'raspberry_id': 'RPI12345',
                                'incident_date': fall_time,
                                'description': 'Fall detected in room number ' + str(room_number),
                                'video_url': sas_url,
                                'status': 'pending'
                            }

                            # Send the POST request to the incidents API
                            incident_response = requests.post(incident_url, json=incident_data)

                            if incident_response.status_code == 201:
                                logging.info("Incident reported successfully.")
                            else:
                                logging.error(f"Failed to report incident. Status code: {incident_response.status_code}")
                                logging.error(f"Error message: {incident_response.text}")
                        else:
                            logging.error(f"Failed to upload video. Status code: {response.status_code}")
                            logging.error("Error: %s", response.text)

                except Exception as e:
                    logging.error(f"Error uploading video: {e}")
            else:
                logging.error(f"Error: Video file {video_file_name} not found.")

    # Display the frame
    cv2.imshow("RGB", frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

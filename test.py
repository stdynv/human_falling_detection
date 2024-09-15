import cv2
import mediapipe as mp
import cvzone
import AzureBlobSorage as az
from collections import deque
import time
import requests
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Raspberry Pi ID and room information
rooms_url = "https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/api/rooms/"
desired_raspberry_id = "RPI12345"  # The Raspberry Pi ID to search for
room_number = '101'

# Initialize BlazePose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture from webcam
cap = cv2.VideoCapture(0)

# Video capture parameters
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Use H.264 codec for better compatibility
buffer_length = int(5 * fps)  # Frames to buffer for 5 seconds
pre_frames = deque(maxlen=buffer_length)

# Control variables for recording after the fall
post_recording = False
post_count = 0
post_length = int(5 * fps)  # Record for 5 seconds after a fall

# Fall detection counter
fall_count = 0

# Cooldown for multiple detections
cooldown_time = 10  # Cooldown in seconds
last_fall_time = 0  # Last detected fall time
cooldown_active = False  # Cooldown state

count = 0
person_count = 0

# Azure Blob Storage details
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=humanfalldata;AccountKey=Bw15KNlxPKxgypqTw/0Wrwz+n8vfNg7KVWuTB6LnFw2c1k5PvUE8nGSk/5ti5Z37+ww5bTY7SCeE+AStxO6ugA==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "videocontainer"

# Initialize Azure Blob Uploader
azure_uploader = az.AzureBlobUploader(CONNECTION_STRING, CONTAINER_NAME)
azure_uploader.ensure_container_exists()

while True:
    ret, frame = cap.read()
    count += 1
    if count % 3 != 0:
        continue
    if not ret:
        break

    # Resize frame to a standard resolution (1280x720)
    frame = cv2.resize(frame, (1280, 720))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_for_recording = frame.copy()

    # Buffer frames before fall detection
    if not post_recording:
        pre_frames.append(frame_for_recording.copy())

    # Perform pose estimation using BlazePose
    results = pose.process(frame_rgb)
    detected_fall = False

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

        # Calculate the distance between shoulders and hips
        shoulder_hip_dist = abs(left_shoulder.y - left_hip.y) + abs(right_shoulder.y - right_hip.y)

        if shoulder_hip_dist < 0.1 and not cooldown_active:
            cvzone.putTextRect(frame, 'Person Fall', (50, 50), 1, 1, colorR=(255, 0, 0))
            detected_fall = True
            current_time = time.time()
            fall_count += 1
            fall_time = time.strftime("%Y-%m-%d %H:%M:%S")
            last_fall_time = current_time
            cooldown_active = True

            # Prepare video and text file names for the fall event
            file_name = f'chute_detectee_{time.strftime("%Y%m%d-%H%M%S")}_room_{room_number}'
            video_file_name = f'{file_name}.mp4'
            

            # Start recording the video of the fall
            if not post_recording:
                out = cv2.VideoWriter(video_file_name, fourcc, fps, (frame.shape[1], frame.shape[0]))
                for f in pre_frames:
                    out.write(f)
                post_recording = True
                post_count = 0

    # Display information on the screen
    info_text = f'Personnes: {person_count} | Chutes: {fall_count} | Chambre: {room_number}'
    cvzone.putTextRect(frame, info_text, (10, 10), scale=1.5, thickness=2, colorT=(0, 0, 0), colorR=(200, 200, 200, 120), offset=10)

    # Check for cooldown expiration
    if cooldown_active and (time.time() - last_fall_time) > cooldown_time:
        cooldown_active = False

    # Write video frames after the fall and stop recording
    if post_recording:
        out.write(frame_for_recording)
        post_count += 1
        if post_count >= post_length:
            post_recording = False
            out.release()

            # Upload the video to Azure Blob Storage
            if os.path.exists(video_file_name):
                try:
                    azure_uploader.upload_video(video_file_name)
                    logging.info(f"Vidéo téléchargée avec succès : {video_file_name}")
                    os.remove(video_file_name)
                    logging.info(f"Fichier vidéo local supprimé : {video_file_name}")
                except Exception as e:
                    logging.error(f"Erreur lors du téléchargement de la vidéo : {e}")
            else:
                logging.error(f"Erreur : le fichier vidéo {video_file_name} est introuvable.")

    # Show the frame
    cv2.imshow("RGB", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

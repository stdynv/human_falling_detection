import cv2
import mediapipe as mp
import cvzone
from collections import deque
import time
import requests
import logging
import os

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)

# URL de l'API pour récupérer les informations des chambres
rooms_url = "https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/api/rooms/"
desired_raspberry_id = "RPI12345"  # ID du Raspberry Pi à rechercher

# Initialiser le numéro de chambre
room_number = None

# Requête GET pour récupérer les données des chambres
try:
    response = requests.get(rooms_url)
    response.raise_for_status()
    rooms_data = response.json()

    # Rechercher le room_number associé au raspberry_id désiré
    for room in rooms_data:
        if room['raspberry_id'] == desired_raspberry_id:
            room_number = room['room_number']
            break

    if room_number:
        logging.info(f"Raspberry ID {desired_raspberry_id} trouvé, numéro de chambre: {room_number}")
    else:
        logging.error(f"Raspberry ID {desired_raspberry_id} introuvable dans les données récupérées.")
        room_number = "Unknown"  # Valeur par défaut si non trouvé

except requests.exceptions.RequestException as e:
    logging.error(f"Erreur lors de la récupération des données des chambres : {e}")
    room_number = "Unknown"  # Valeur par défaut en cas d'erreur

# Initialiser BlazePose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialiser la capture vidéo depuis la webcam
cap = cv2.VideoCapture(0)

# Définir les paramètres pour l'enregistrement des séquences
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Utiliser un codec compatible
buffer_length = int(5 * fps)  # Nombre de frames pour 5 secondes
pre_frames = deque(maxlen=buffer_length)

# Variables de contrôle pour l'enregistrement après la chute
post_recording = False
post_count = 0
post_length = int(5 * fps)  # Nombre de frames pour 5 secondes après la chute

# Compteur de chutes
fall_count = 0

# Cooldown pour éviter les détections multiples
cooldown_time = 10  # Temps de cooldown en secondes
last_fall_time = 0  # Dernière chute détectée
cooldown_active = False  # Indicateur si le cooldown est actif

count = 0
person_count = 0

# URL de l'API pour télécharger les vidéos sur Azure et enregistrer les incidents
upload_url = "https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/api/azure/upload"
incident_url = 'https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/api/incidents/create'

while True:
    ret, frame = cap.read()
    count += 1
    if count % 3 != 0:
        continue
    if not ret:
        break

    frame = cv2.resize(frame, (1020, 600))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_for_recording = frame.copy()

    # Enregistrer les frames avant la détection de chute
    if not post_recording:
        pre_frames.append(frame_for_recording.copy())

    # Effectuer l'estimation de pose avec BlazePose
    results = pose.process(frame_rgb)

    detected_fall = False

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

        shoulder_hip_dist = abs(left_shoulder.y - left_hip.y) + abs(right_shoulder.y - right_hip.y)

        if shoulder_hip_dist < 0.1 and not cooldown_active:
            cvzone.putTextRect(frame, 'Person Fall', (50, 50), 1, 1, colorR=(255, 0, 0))
            detected_fall = True
            current_time = time.time()
            fall_count += 1
            fall_time = time.strftime("%Y-%m-%d %H:%M:%S")
            last_fall_time = current_time
            cooldown_active = True

            file_name = f'chute_detectee_{time.strftime("%Y%m%d-%H%M%S")}_room_{room_number}'
            video_file_name = f'{file_name}.mp4'
            text_file_name = f'{file_name}.txt'

            with open(text_file_name, 'w') as f:
                f.write(f"Nombre de personnes présentes : {person_count}\n")
                f.write(f"Numéro de la chambre : {room_number}\n")
                f.write(f"Heure de la chute : {fall_time}\n")

            if not post_recording:
                out = cv2.VideoWriter(video_file_name, fourcc, fps, (frame.shape[1], frame.shape[0]))
                for f in pre_frames:
                    out.write(f)
                post_recording = True
                post_count = 0

    info_text = f'Personnes: {person_count} | Chutes: {fall_count} | Chambre: {room_number}'
    cvzone.putTextRect(frame, info_text, (10, 10), scale=1.5, thickness=2, colorT=(0, 0, 0), colorR=(200, 200, 200, 120), offset=10)

    if cooldown_active and (time.time() - last_fall_time) > cooldown_time:
        cooldown_active = False

    if post_recording:
        out.write(frame_for_recording)
        post_count += 1
        if post_count >= post_length:
            post_recording = False
            out.release()

            if os.path.exists(video_file_name):
                try:
                    with open(video_file_name, 'rb') as video_file:
                        files = {'video': (video_file_name, video_file, 'video/mp4')}
                        response = requests.post(upload_url, files=files)

                        if response.status_code == 200:
                            logging.info("Vidéo téléchargée avec succès.")
                            sas_url = response.json().get("sas_url")

                            incident_data = {
                                'raspberry_id': desired_raspberry_id,
                                'incident_date': fall_time,
                                'description': f'Fall detected in room {room_number}',
                                'video_url': sas_url,
                                'status': 'pending'
                            }

                            incident_response = requests.post(incident_url, json=incident_data)

                            if incident_response.status_code == 201:
                                logging.info("Incident signalé avec succès.")
                            else:
                                logging.error(f"Erreur lors de la signalisation de l'incident : {incident_response.text}")
                        else:
                            logging.error(f"Échec du téléchargement de la vidéo : {response.text}")

                except Exception as e:
                    logging.error(f"Erreur lors du téléchargement de la vidéo : {e}")
            else:
                logging.error(f"Erreur : le fichier vidéo {video_file_name} est introuvable.")

    cv2.imshow("RGB", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
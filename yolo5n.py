from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import pandas as pd
import cvzone
from collections import deque
import time
import mediapipe as mp
import torch
import warnings
import random

warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')

# Configurer PyTorch pour utiliser le CPU globalement
torch.device('cpu')

# Charger un modèle YOLOv8 Nano optimisé pour des dispositifs embarqués
model = YOLO("yolov8n.pt")  # Assurez-vous que ce modèle est téléchargé et accessible

# Initialiser la liste des classes à partir du fichier coco.txt
with open("coco.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

# Initialiser Mediapipe pour la détection de pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialiser la caméra Picamera2
picam2 = Picamera2()
picam2.start()

# Définir les paramètres pour l'enregistrement des séquences
fps = 10  # Limiter le FPS pour réduire la charge
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# File pour garder les frames avant la chute (5 secondes avant)
buffer_length = int(5 * fps)  # Nombre de frames pour 5 secondes
pre_frames = deque(maxlen=buffer_length)

# Variables de contrôle pour l'enregistrement après la chute
post_recording = False
post_count = 0
post_length = int(5 * fps)  # Nombre de frames pour 5 secondes après la chute

# Compteur pour optimiser le traitement des frames
count = 0

# Variables pour le suivi de la position et de la taille
previous_positions = deque(maxlen=5)  # Sauvegarder les positions précédentes

# Compteur de chutes et informations de la chambre
fall_count = 0
room_number = random.randint(1, 100)  # Générer un numéro de chambre initialement

# Cooldown pour éviter les détections multiples
cooldown_time = 5  # Temps de cooldown en secondes
last_fall_time = 0  # Dernière chute détectée

while True:
    # Capture de l'image depuis Picamera2
    frame = picam2.capture_array()
    count += 1

    # Traiter seulement une frame sur trois pour alléger la charge
    if count % 3 != 0:
        continue

    frame = cv2.resize(frame, (640, 480))  # Utiliser une résolution plus basse pour alléger le traitement
    frame_for_recording = frame.copy()  # Copie pour l'enregistrement sans annotations

    # Enregistrer les frames avant la détection de chute
    if not post_recording:
        pre_frames.append(frame_for_recording)

    # Effectuer les prédictions avec YOLOv8 Nano
    results = model(frame)

    # Vérifiez si le modèle a détecté des boîtes
    if len(results[0].boxes) == 0:
        cv2.putText(frame, 'Aucune detection', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("RGB", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")

    # Compter le nombre de personnes présentes dans la frame
    person_count = sum(1 for _, row in px.iterrows() if class_list[int(row[5])] == 'person')

    # Détecter la position du lit
    bed_detected = False
    bed_box = None

    for _, row in px.iterrows():
        x1, y1, x2, y2 = map(int, row[:4])
        confidence = row[4]
        d = int(row[5])
        c = class_list[d]

        # Vérifier si un lit est détecté
        if c == 'bed':
            bed_detected = True
            bed_box = (x1, y1, x2, y2)

        # Ignorer les détections faibles
        if confidence < 0.5:
            continue

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Calcul pour détecter une chute
        if 'person' in c:
            h, w = y2 - y1, x2 - x1
            aspect_ratio = h / w
            area = h * w
            
            # Sauvegarder la position actuelle de la personne
            current_position = (x1 + x2) // 2, y2
            previous_positions.append(current_position)

            # Ignorer les chutes quand la personne est trop proche
            if area > 40000:
                cvzone.putTextRect(frame, "Person too close, ignoring fall", (x1, y1 - 60), 1, 1, colorR=(0, 0, 255))
                continue

            # Vérifier si la personne est sur un lit détecté
            if bed_detected and bed_box:
                bx1, by1, bx2, by2 = bed_box
                if x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1:
                    cvzone.putTextRect(frame, "Person on bed, ignoring fall", (x1, y1 - 60), 1, 1, colorR=(0, 0, 255))
                    continue

            # Vérifier le mouvement vertical rapide
            vertical_speeds = [previous_positions[i][1] - previous_positions[i - 1][1] for i in range(1, len(previous_positions))]
            avg_speed = sum(vertical_speeds) / len(vertical_speeds) if vertical_speeds else 0

            # Vérifier si le cooldown est terminé
            current_time = time.time()
            if aspect_ratio < 1.2 and avg_speed > 10 and (current_time - last_fall_time) > cooldown_time:
                fall_count += 1
                room_number = random.randint(1, 100)
                fall_time = time.strftime("%Y-%m-%d %H:%M:%S")
                last_fall_time = current_time

                # Enregistrer les informations de la chute
                file_name = f'chute_detectee_{time.strftime("%Y%m%d-%H%M%S")}_room_{room_number}'
                with open(f'{file_name}.txt', 'w') as f:
                    f.write(f"Nombre de personnes présentes : {person_count}\n")
                    f.write(f"Numéro de la chambre : {room_number}\n")
                    f.write(f"Heure de la chute : {fall_time}\n")

                # Démarrer l'enregistrement 5 secondes avant et après la chute
                if not post_recording:
                    out = cv2.VideoWriter(f'{file_name}.avi', fourcc, fps, (frame.shape[1], frame.shape[0]))
                    for f in pre_frames:
                        out.write(f)
                    post_recording = True
                    post_count = 0

    # Afficher les informations en haut à gauche de l'écran
    info_text = f'Personnes: {person_count} | Chutes: {fall_count} | Chambre: {room_number}'
    cvzone.putTextRect(frame, info_text, (10, 10), scale=1.5, thickness=2, colorT=(0, 0, 0), colorR=(200, 200, 200, 120), offset=10)

    # Enregistrer les frames après la détection de chute (sans annotations)
    if post_recording:
        out.write(frame_for_recording)
        post_count += 1
        if post_count >= post_length:
            post_recording = False
            out.release()

    cv2.imshow("RGB", frame)

    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop()
cv2.destroyAllWindows()

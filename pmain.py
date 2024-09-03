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
my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")

# Initialiser Mediapipe pour la détection de pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialiser la capture vidéo depuis la webcam
cap = cv2.VideoCapture(0)

# Définir les paramètres pour l'enregistrement des séquences
fps = cap.get(cv2.CAP_PROP_FPS)
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
    ret, frame = cap.read()
    count += 1

    # Passer toutes les deux frames pour optimiser la vitesse de traitement
    if count % 2 != 0:
        continue

    if not ret:
        break

    frame = cv2.resize(frame, (1020, 600))
    frame_for_recording = frame.copy()  # Copie pour l'enregistrement sans annotations

    # Enregistrer les frames avant la détection de chute
    if not post_recording:
        pre_frames.append(frame_for_recording.copy())

    # Effectuer les prédictions avec YOLOv8 Nano
    results = model(frame)  # YOLOv8 Nano est optimisé pour le CPU et rapide sur le Raspberry Pi

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
    person_count = sum(1 for index, row in px.iterrows() if class_list[int(row[5])] == 'person')

    # Détecter la position des lits et canapés
    bed_couch_boxes = []  # Liste pour stocker les positions des lits et canapés

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])

        d = int(row[5])
        c = class_list[d]

        # Vérifier si un lit ou un canapé est détecté
        if c in ['bed', 'couch']:
            bed_couch_boxes.append((x1, y1, x2, y2))  # Sauvegarder la position du lit ou canapé

        # Utiliser un seuil de confiance pour ignorer les détections faibles
        confidence = row[4]
        if confidence < 0.5:  # Ajustez ce seuil en fonction de la fiabilité nécessaire
            continue

        cvzone.putTextRect(frame, f'{c} {confidence:.2f}', (x1, y1), 1, 1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Calcul pour détecter une chute
        if 'person' in c:
            h = y2 - y1
            w = x2 - x1
            aspect_ratio = h / w
            area = h * w  # Surface de la boîte englobante
            
            # Affichage de débogage pour vérifier les valeurs
            cvzone.putTextRect(frame, f'Aspect Ratio: {aspect_ratio:.2f}', (x1, y1 - 30), 1, 1, colorR=(255, 255, 0))
            
            # Sauvegarder la position actuelle de la personne
            current_position = (x1 + x2) // 2, y2
            previous_positions.append(current_position)

            # Critère supplémentaire pour ignorer les chutes quand la personne est trop proche
            if area > 100000:  # Ajustez ce seuil selon la taille typique lorsque vous êtes proche de la caméra
                cvzone.putTextRect(frame, "Person too close, ignoring fall", (x1, y1 - 60), 1, 1, colorR=(0, 0, 255))
                continue

            # Vérifier si la personne est sur un lit ou un canapé détecté
            on_bed_or_couch = False
            for bx1, by1, bx2, by2 in bed_couch_boxes:
                # Vérifier si la personne chevauche un lit ou un canapé
                if x1 < bx2 and x2 > bx1 and y1 < by2 and y2 > by1:
                    on_bed_or_couch = True
                    break

            if on_bed_or_couch:
                cvzone.putTextRect(frame, "Person on bed/couch, ignoring fall", (x1, y1 - 60), 1, 1, colorR=(0, 0, 255))
                continue

            # Découper la partie de l'image correspondant à la personne détectée
            person_frame = frame[y1:y2, x1:x2]

            # Convertir en RGB pour Mediapipe
            person_rgb = cv2.cvtColor(person_frame, cv2.COLOR_BGR2RGB)

            # Obtenir la détection de pose
            results_pose = pose.process(person_rgb)

            # Dessiner le squelette si une pose est détectée (uniquement sur l'affichage)
            if results_pose.pose_landmarks:
                mp_drawing.draw_landmarks(
                    person_frame, 
                    results_pose.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

            # Remettre la partie modifiée dans le frame original
            frame[y1:y2, x1:x2] = person_frame

            # Critère d'orientation avec un seuil d'aspect ratio ajustable
            if aspect_ratio < 1.2:  # Ajustez ce seuil selon votre situation
                # Vérifier le mouvement vertical rapide
                vertical_speeds = [previous_positions[i][1] - previous_positions[i - 1][1] for i in range(1, len(previous_positions))]
                avg_speed = sum(vertical_speeds) / len(vertical_speeds) if vertical_speeds else 0

                # Affichage des vitesses pour debug
                cvzone.putTextRect(frame, f'Speed: {avg_speed:.2f}', (x1, y1 - 60), 1, 1, colorR=(0, 255, 255))
                
                # Vérifier si le cooldown est terminé
                current_time = time.time()
                if avg_speed > 10 and (current_time - last_fall_time) > cooldown_time:  # Ajustez ce seuil
                    fall_count += 1  # Incrémenter le compteur de chutes
                    room_number = random.randint(1, 100)  # Générer un numéro de chambre aléatoire
                    fall_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Heure de la chute

                    # Mettre à jour le temps de la dernière chute détectée
                    last_fall_time = current_time

                    # Afficher le compteur de chutes et le numéro de chambre
                    cvzone.putTextRect(frame, f'Fall Detected! Count: {fall_count}, Room: {room_number}', (x1, y1 - 90), 1, 1, colorR=(255, 0, 0))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    # Nom du fichier vidéo et du fichier texte
                    file_name = f'chute_detectee_{time.strftime("%Y%m%d-%H%M%S")}_room_{room_number}'
                    video_file_name = f'{file_name}.avi'
                    text_file_name = f'{file_name}.txt'

                    # Créer et écrire les informations dans le fichier texte
                    with open(text_file_name, 'w') as f:
                        f.write(f"Nombre de personnes présentes : {person_count}\n")
                        f.write(f"Numéro de la chambre : {room_number}\n")
                        f.write(f"Heure de la chute : {fall_time}\n")

                    # Démarrer l'enregistrement 5 secondes avant et après la chute
                    if not post_recording:
                        # Créer le fichier vidéo pour enregistrer la chute
                        out = cv2.VideoWriter(video_file_name, fourcc, fps, (frame.shape[1], frame.shape[0]))

                        # Enregistrer les frames des 5 secondes avant la chute
                        for f in pre_frames:
                            out.write(f)

                        # Démarrer l'enregistrement des frames après la chute
                        post_recording = True
                        post_count = 0

    # Afficher les informations en haut à gauche de l'écran avec un fond gris clair et texte noir
    info_text = f'Personnes: {person_count} | Chutes: {fall_count} | Chambre: {room_number}'
    cvzone.putTextRect(frame, info_text, (10, 10), scale=1.5, thickness=2, colorT=(0, 0, 0), colorR=(200, 200, 200, 120), offset=10)

    # Enregistrer les frames après la détection de chute (sans annotations)
    if post_recording:
        out.write(frame_for_recording)  # Utiliser la copie sans les annotations
        post_count += 1
        if post_count >= post_length:
            post_recording = False
            out.release()

    cv2.imshow("RGB", frame)

    # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

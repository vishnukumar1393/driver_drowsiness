import cv2
import numpy as np
import mediapipe as mp
import math
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
UPPER_LIP = 13
LOWER_LIP = 14
def calculate_ear(landmarks, eye_points, img_w, img_h):
    p = [landmarks[i] for i in eye_points]
    coords = [(int(p_.x * img_w), int(p_.y * img_h)) for p_ in p]
    A = np.linalg.norm(np.array(coords[1]) - np.array(coords[5]))
    B = np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))
    C = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
    return (A + B) / (2.0 * C)
def detect_yawn(landmarks, img_w, img_h):
    top_lip = landmarks[UPPER_LIP]
    bottom_lip = landmarks[LOWER_LIP]
    top = np.array([top_lip.x * img_w, top_lip.y * img_h])
    bottom = np.array([bottom_lip.x * img_w, bottom_lip.y * img_h])
    distance = np.linalg.norm(top - bottom)
    return distance > 30  # Adjust if needed
cap = cv2.VideoCapture(0)
drowsy_frames = 0
EAR_THRESHOLD = 0.25
DROWSY_LIMIT = 15
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_h, img_w = frame.shape[:2]
    results = face_mesh.process(frame_rgb)
    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            lm = landmarks.landmark
            left_ear = calculate_ear(lm, LEFT_EYE, img_w, img_h)
            right_ear = calculate_ear(lm, RIGHT_EYE, img_w, img_h)
            avg_ear = (left_ear + right_ear) / 2.0
            is_yawning = detect_yawn(lm, img_w, img_h)
            is_eyes_closed = avg_ear < EAR_THRESHOLD
            if is_eyes_closed or is_yawning:
                drowsy_frames += 1
            else:
                drowsy_frames = 0
            if drowsy_frames >= DROWSY_LIMIT:
                cv2.putText(frame, "DROWSINESS ALERT!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
                if is_eyes_closed:
                    cv2.putText(frame, "Eyes Closed", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                if is_yawning:
                    cv2.putText(frame, "Yawning Detected", (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow('Driver Drowsiness Detection', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import websocket
import json
import time
import numpy as np

#WebSocket Setup
WS_URL = "ws://localhost:8081/sensor"
ws = websocket.WebSocket()
ws.connect(WS_URL)
print("Verbunden mit WebSocket-Server")

# MediaPipe FaceMesh
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

#Kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
print("Kamera gestartet – drücke 'q' zum Beenden")

# 3D Modellpunkte (Nase, Kinn, Augenwinkel, Mundwinkel)
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nase
    (0.0, -330.0, -65.0),        # Kinn
    (-225.0, 170.0, -135.0),     # linkes Auge
    (225.0, 170.0, -135.0),      # rechtes Auge
    (-150.0, -150.0, -125.0),    # linker Mundwinkel
    (150.0, -150.0, -125.0)      # rechter Mundwinkel
], dtype=np.float64)

prev_time = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    h, w = frame.shape[:2]

    if results.multi_face_landmarks:
        #FaceMesh zeichnen
        for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face.FACEMESH_TESSELATION,  # alle Dreiecke
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face.FACEMESH_CONTOURS,     # Konturen (Augen, Lippen etc.)
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )

        #Hauptgesichtspunkte für PnP
        face_landmarks = results.multi_face_landmarks[0].landmark

        image_points = np.array([
            (face_landmarks[1].x * w, face_landmarks[1].y * h),    # Nase
            (face_landmarks[152].x * w, face_landmarks[152].y * h), # Kinn
            (face_landmarks[263].x * w, face_landmarks[263].y * h), # rechtes Auge
            (face_landmarks[33].x * w, face_landmarks[33].y * h),   # linkes Auge
            (face_landmarks[287].x * w, face_landmarks[287].y * h), # rechter Mundwinkel
            (face_landmarks[57].x * w, face_landmarks[57].y * h)    # linker Mundwinkel
        ], dtype=np.float64)

        # Kamera-Matrix & Verzerrung
        focal_length = w
        center = (w / 2, h / 2)
        cam_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1))

        #Kopfpose berechnen
        success, rotation_vec, translation_vec = cv2.solvePnP(
            MODEL_POINTS, image_points, cam_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        # Rotationsmatrix → Eulerwinkel
        rmat, _ = cv2.Rodrigues(rotation_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        pitch, yaw, roll = angles

        data = {
            "head_rotation": {"x": float(pitch), "y": float(yaw), "z": float(roll)},
            "ts": time.time()
        }

        ws.send(json.dumps(data))

        #Debug Overlay
        cv2.putText(frame, f"Pitch: {pitch:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Yaw: {yaw:.2f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Roll: {roll:.2f}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face Mesh Head Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
ws.close()
cv2.destroyAllWindows()
print("Beendet")
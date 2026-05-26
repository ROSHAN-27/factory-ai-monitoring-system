# -------------------- SILENCE LOGS --------------------
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings("ignore")

# -------------------- IMPORTS --------------------
import cv2
from deepface import DeepFace
from datetime import datetime

# -------------------- CONFIG --------------------
CAMERA_SOURCE = 0
EVENT_TYPE = "IN"

FRAME_SKIP = 5
COOLDOWN = 30

LOG_FILE = "attendance.csv"

# -------------------- START CAMERA --------------------
cap = cv2.VideoCapture(CAMERA_SOURCE)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

frame_count = 0

# Store last detection time
last_detected = {}

print("ENTRY CAMERA STARTED")

# -------------------- LOG FUNCTION --------------------
def save_log(name):

    now = datetime.now()

    # Prevent duplicate logs
    if name in last_detected:

        seconds = (now - last_detected[name]).seconds

        if seconds < COOLDOWN:
            return

    last_detected[name] = now

    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as f:
        f.write(f"{name},{EVENT_TYPE},{timestamp}\n")

    print(f"{name} {EVENT_TYPE}")

# -------------------- MAIN LOOP --------------------
while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    frame_count += 1

    # Resize frame
    frame = cv2.resize(frame, (800, 600))

    # Process only some frames
    if frame_count % FRAME_SKIP == 0:

        try:

            # Detect faces
            faces = DeepFace.extract_faces(
                img_path=frame,
                enforce_detection=False,
                detector_backend='opencv'
            )

            for face in faces:

                facial_area = face['facial_area']

                x = facial_area['x']
                y = facial_area['y']
                w = facial_area['w']
                h = facial_area['h']

                # Draw rectangle
                cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

                # Crop only face
                face_crop = frame[y:y+h, x:x+w]

                # Face recognition
                dfs = DeepFace.find(
                    img_path=face_crop,
                    db_path="dataset",
                    enforce_detection=False,
                    silent=True
                )

                # Match found
                if len(dfs[0]) > 0:

                    identity = dfs[0].iloc[0]['identity']

                    name = identity.split("\\")[-1].split(".")[0]

                    # Display name
                    cv2.putText(frame, name, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0,255,0), 2)

                    # Save attendance
                    save_log(name)

                else:

                    cv2.putText(frame, "Unknown", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0,0,255), 2)

        except Exception as e:
            print("Detection Error:", e)

    # Show window
    cv2.imshow("ENTRY CAMERA", frame)

    # ESC to close
    key = cv2.waitKey(1)

    if key == 27:
        break

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()
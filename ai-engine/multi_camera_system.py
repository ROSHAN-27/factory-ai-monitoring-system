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
from database import save_attendance

# -------------------- CAMERA CONFIG --------------------

ENTRY_CAMERA = 0

# -------------------- PERFORMANCE --------------------

FRAME_SKIP = 5
COOLDOWN = 30

# -------------------- START CAMERA --------------------

entry_cap = cv2.VideoCapture(ENTRY_CAMERA)

if not entry_cap.isOpened():
    print("ENTRY CAMERA NOT OPENED")
    exit()

print("ENTRY CAMERA SYSTEM STARTED")

# -------------------- VARIABLES --------------------

frame_count = 0
last_logged = {}

# -------------------- PROCESS FRAME --------------------

def process_frame(frame, event_type, camera_name):

    global last_logged

    try:

        dfs = DeepFace.find(
            img_path=frame,
            db_path="dataset",
            enforce_detection=False,
            silent=True,
            detector_backend="opencv"
        )

        if len(dfs[0]) > 0:

            identity = dfs[0].iloc[0]['identity']

            name = identity.split("\\")[-1].split(".")[0]

            now = datetime.now()

            # ---------------- COOLDOWN ----------------

            if name in last_logged:

                seconds = (now - last_logged[name]).seconds

                if seconds < COOLDOWN:
                    return frame

            last_logged[name] = now

            # ---------------- TERMINAL OUTPUT ----------------

            print(f"{name} {event_type}")

            # ---------------- SAVE TO POSTGRESQL ----------------

            save_attendance(name, event_type, camera_name)

            # ---------------- DISPLAY ----------------

            cv2.putText(
                frame,
                f"{name} {event_type}",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    except Exception as e:

        print("Detection Error:", e)

    return frame

# -------------------- MAIN LOOP --------------------

while True:

    ret, frame = entry_cap.read()

    if not ret:
        print("Camera read failed")
        break

    frame_count += 1

    # Resize for performance
    frame = cv2.resize(frame, (640, 480))

    if frame_count % FRAME_SKIP == 0:

        frame = process_frame(
            frame,
            "IN",
            "ENTRY_CAMERA"
        )

    # Camera title

    cv2.putText(
        frame,
        "ENTRY CAMERA",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2
    )

    # Show camera

    cv2.imshow("ENTRY CAMERA", frame)

    # ESC to exit

    if cv2.waitKey(1) == 27:
        break

# -------------------- CLEANUP --------------------

entry_cap.release()

cv2.destroyAllWindows()
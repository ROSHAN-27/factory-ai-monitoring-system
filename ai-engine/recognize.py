# -------------------- SILENCE LOGS --------------------
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import contextlib

# -------------------- IMPORTS --------------------
import cv2
from deepface import DeepFace
from datetime import datetime

# Import camera config
from camera_config import ENTRY_CAMERA

# -------------------- CONFIG --------------------
LOG_FILE = "attendance.csv"

FRAME_SKIP = 10
COOLDOWN = 60
ABSENCE_RESET = 5

frame_count = 0
last_name = "No Face"

# Track states
last_seen_time = {}
last_logged_time = {}

# -------------------- CAMERA SOURCE --------------------

# CURRENTLY USING WEBCAM
CAMERA_SOURCE = 0

# LATER FOR NETWORK CAMERA:
# CAMERA_SOURCE = ENTRY_CAMERA

# -------------------- FUNCTION --------------------
def mark_attendance(name):
    now = datetime.now()

    # Prevent duplicate logs
    if name in last_logged_time:
        if (now - last_logged_time[name]).seconds < COOLDOWN:
            return

    last_logged_time[name] = now

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    with open(LOG_FILE, "a") as f:
        f.write(f"{name},{date},{time}\n")

    print(f"[LOGGED] {name} at {time}")

# -------------------- START CAMERA --------------------
cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# -------------------- MAIN LOOP --------------------
while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        continue

    # Resize for performance
    frame = cv2.resize(frame, (900, 600))

    frame_count += 1

    # Process every Nth frame
    if frame_count % FRAME_SKIP == 0:

        try:
            # Hide DeepFace console logs
            with open(os.devnull, 'w') as f, \
                 contextlib.redirect_stdout(f), \
                 contextlib.redirect_stderr(f):

                result = DeepFace.find(
                    img_path=frame,
                    db_path="dataset",
                    enforce_detection=False,
                    silent=True
                )

            # Face found
            if len(result[0]) > 0:

                name = result[0].iloc[0]['identity']
                name = name.split("\\")[-1].split(".")[0]

                last_name = name

                now = datetime.now()

                # Re-entry detection
                if name in last_seen_time:

                    if (now - last_seen_time[name]).seconds > ABSENCE_RESET:
                        mark_attendance(name)

                else:
                    mark_attendance(name)

                last_seen_time[name] = now

            else:
                last_name = "Unknown"

        except:
            last_name = "No Face"

    # -------------------- DISPLAY --------------------
    cv2.putText(
        frame,
        last_name,
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Face Recognition System", frame)

    # ESC to exit
    if cv2.waitKey(1) == 27:
        break

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()
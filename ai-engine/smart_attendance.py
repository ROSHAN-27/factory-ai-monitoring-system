# -------------------- SILENCE LOGS --------------------
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# -------------------- IMPORTS --------------------
import cv2
from deepface import DeepFace
from datetime import datetime

# -------------------- CAMERA --------------------
cap = cv2.VideoCapture(0)

# -------------------- CONFIG --------------------
GREEN_LINE_Y = 200
RED_LINE_Y = 400
OFFSET = 20
FRAME_SKIP = 20

frame_count = 0

# Prevent duplicate logs
person_states = {}

# -------------------- LOG FUNCTION --------------------
def log_event(name, status):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    print(f"{name} {status}")

    with open("attendance.csv", "a") as f:
        f.write(f"{name},{status},{date},{time}\n")

# -------------------- MAIN LOOP --------------------
while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    frame_count += 1

    # -------------------- DRAW LINES --------------------
    cv2.line(frame, (0, GREEN_LINE_Y), (900, GREEN_LINE_Y), (0,255,0), 3)
    cv2.line(frame, (0, RED_LINE_Y), (900, RED_LINE_Y), (0,0,255), 3)

    cv2.putText(frame, "GREEN = IN", (20, 190),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.putText(frame, "RED = OUT", (20, 390),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    # -------------------- PROCESS --------------------
    if frame_count % FRAME_SKIP == 60:

        try:

            # -------------------- FACE RECOGNITION --------------------
            result = DeepFace.find(
                img_path=frame,
                db_path="dataset",
                enforce_detection=False,
                silent=True
            )

            if len(result[0]) > 0:

                # -------------------- GET NAME --------------------
                name = result[0].iloc[0]['identity']
                name = name.split("\\")[-1].split(".")[0]

                # -------------------- FACE DETECTION --------------------
                face_objs = DeepFace.extract_faces(
                    img_path=frame,
                    detector_backend='opencv',
                    enforce_detection=False
                )

                if len(face_objs) > 0:

                    face = face_objs[0]

                    facial_area = face['facial_area']

                    x = facial_area['x']
                    y = facial_area['y']
                    w = facial_area['w']
                    h = facial_area['h']

                    center_y = int(y + h / 2)

                    # -------------------- DRAW FACE BOX --------------------
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

                    cv2.putText(frame, name, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0,255,0), 2)

                    # -------------------- IN DETECTION --------------------
                    if GREEN_LINE_Y - OFFSET < center_y < GREEN_LINE_Y + OFFSET:

                        if person_states.get(name) != "IN":

                            person_states[name] = "IN"

                            log_event(name, "IN")

                    # -------------------- OUT DETECTION --------------------
                    if RED_LINE_Y - OFFSET < center_y < RED_LINE_Y + OFFSET:

                        if person_states.get(name) != "OUT":

                            person_states[name] = "OUT"

                            log_event(name, "OUT")

        except Exception as e:
            print("ERROR:", e)

    # -------------------- DISPLAY --------------------
    cv2.imshow("Smart Attendance System", frame)

    # ESC to exit
    if cv2.waitKey(1) == 27:
        break

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()
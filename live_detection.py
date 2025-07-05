# live_detection.py

from utils.meter_tracker import MeterTracker
from utils.helper import format_timestamp, save_image, generate_defect_filename
from utils.sql_connector import insert_defect
from ultralytics import YOLO
from config import MODEL_PATH, DEFAULT_SPEED, REPORT_DIR

import cv2
import os

def run_live_detection(sheet_id, stop_callback=None, show_alert_callback=None):
    model = YOLO(MODEL_PATH)
    tracker = MeterTracker(sheet_number=sheet_id, speed_m_per_sec=50.0) 
    tracker.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not detected.")
        return []

    defects = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed.")
            break

        results = model(frame, imgsz=640, conf=0.4)# have to change when i got the actual data

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                defect_type = model.names[cls_id]
                timestamp = format_timestamp()
                length_m = tracker.get_length()

                defect_filename = generate_defect_filename(sheet_id, defect_type)
                image_path = os.path.join(REPORT_DIR, sheet_id, "images", defect_filename)
                save_image(frame, image_path)

                defect_info = {
                    'defect_type': defect_type,
                    'timestamp': timestamp,
                    'length_m': length_m,
                    'image_path': image_path
                }

                defects.append(defect_info)
                insert_defect(sheet_id, defect_type, length_m, image_path)

                # ✅ GUI alert
                if show_alert_callback:
                    show_alert_callback(defect_info)

        annotated_frame = results[0].plot()
        cv2.putText(
            annotated_frame,
            f"Length: {tracker.get_length():.2f} m",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        cv2.imshow("Steel Inspector", annotated_frame)

        # Exit when GUI signals stop
        if stop_callback and stop_callback():
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Stopping due to 'q' key press.")
            break

    tracker.stop()
    cap.release()
    cv2.destroyAllWindows()

    return defects

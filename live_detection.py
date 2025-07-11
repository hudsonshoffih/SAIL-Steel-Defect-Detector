import os
import cv2
from ultralytics import YOLO

from utils.meter_tracker import MeterTracker
from utils.helper import format_timestamp, save_image, generate_defect_filename
from utils.sql_connector import insert_defect
from config import MODEL_PATH, DEFAULT_SPEED, REPORT_DIR, CONF_THRESHOLD  # add CONF_THRESHOLD in config.py

# --------------------------------------------------------------------
def run_live_detection(
        sheet_id: str,
        speed_mps: float | None = None,
        stop_callback=None,
        show_alert_callback=None,
        conf: float | None = None,
        ):
    """
    Run YOLO live detection in a loop.
    Args
        sheet_id                : coil/sheet identifier string
        speed_mps (optional)    : conveyor speed (m/s); if None → DEFAULT_SPEED
        stop_callback (func)    : returns True when GUI/user wants to stop
        show_alert_callback     : called with defect_info dict when a defect detected
        conf (float, optional)  : confidence threshold (default from config)
    Returns
        list[dict] defects      : collected defect dictionaries
    """

    model = YOLO(MODEL_PATH)
    speed = speed_mps if speed_mps is not None else DEFAULT_SPEED
    conf_thr = conf if conf is not None else CONF_THRESHOLD

    tracker = MeterTracker(sheet_number=sheet_id, speed_m_per_sec=speed)
    tracker.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not detected.")
        return []

    defects: list[dict] = []

    print("🔍 Live detection started — press 'q' or Stop button to end.")
    while True:
        # Quick exit if GUI sets stop flag BEFORE grabbing next frame
        if stop_callback and stop_callback():
            break

        ret, frame = cap.read()
        if not ret:
            print("⚠️ Camera read failed.")
            break

        # YOLO inference
        results = model(frame, imgsz=640, conf=conf_thr)

        # Parse detections
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf_score = float(box.conf[0])
                defect_type = model.names[cls_id]
                timestamp = format_timestamp()
                length_m = tracker.get_length()

                defect_filename = generate_defect_filename(sheet_id, defect_type)
                image_path = os.path.join(REPORT_DIR, sheet_id, "images", defect_filename)
                save_image(frame, image_path)

                defect_info = {
                    "defect_type": defect_type,
                    "timestamp" : timestamp,
                    "length_m"  : length_m,
                    "image_path": image_path,
                    "confidence": conf_score,
                }

                defects.append(defect_info)
                insert_defect(sheet_id, defect_type, length_m, image_path)

                if show_alert_callback:
                    show_alert_callback(defect_info)

        # Draw overlay
        annotated = results[0].plot()
        cv2.putText(
            annotated, f"Length: {tracker.get_length():.2f} m",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        cv2.imshow("Steel Inspector (press 'q' to exit)", annotated)

        # Check stop flags after display
        if stop_callback and stop_callback():
            break
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("🛑 Stopping via 'q' key.")
            break

    # Cleanup
    tracker.stop()
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Live detection ended.")
    return defects

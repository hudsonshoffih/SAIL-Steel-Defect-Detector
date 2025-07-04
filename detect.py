# detect.py

import cv2
import time
import os
from datetime import datetime
from ultralytics import YOLO

def run_detection(sheet_id, model_path="model/best.pt", save_path="reports", speed_mps=50):
    model = YOLO(model_path)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot open webcam.")
        return []

    print(f"📷 Starting detection for Sheet ID: {sheet_id}")
    os.makedirs(f"{save_path}/{sheet_id}/images", exist_ok=True)

    defect_log = []
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to capture frame.")
            break

        # Predict using YOLOv8
        results = model(frame, imgsz=640, conf=0.4)
        boxes = results[0].boxes
        detected = False

        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            defect_type = model.names[cls_id]

            # Calculate time + estimated length
            elapsed_time = time.time() - start_time
            approx_length = round(elapsed_time * speed_mps, 2)
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Crop and save defect region
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped = frame[y1:y2, x1:x2]
            img_filename = f"{defect_type}_{timestamp.replace(':', '-')}.jpg"
            img_path = os.path.join(save_path, sheet_id, "images", img_filename)
            cv2.imwrite(img_path, cropped)

            print(f"✅ Detected: {defect_type} at {approx_length}m [{timestamp}]")

            defect_log.append({
                "sheet_id": sheet_id,
                "defect_type": defect_type,
                "timestamp": timestamp,
                "length_m": approx_length,
                "image_path": img_path
            })

            detected = True

        # Show annotated frame
        annotated = results[0].plot()
        cv2.imshow("🛠️ Steel Sheet Detection", annotated)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("🛑 Detection stopped.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return defect_log

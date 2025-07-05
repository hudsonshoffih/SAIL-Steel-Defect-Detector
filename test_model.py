# test_model.py

import sys
import os
import cv2
from ultralytics import YOLO
from utils.helper import format_timestamp, generate_defect_filename, save_image
from utils.sql_connector import insert_defect

# CONFIG
MODEL_PATH = "runs/detect/train5/weights/best.pt"
SHEET_ID = "test_sheet"

# ✅ Check for image path argument
if len(sys.argv) < 2:
    print("❌ Please provide the path to the test image:\nUsage: python test_model.py /path/to/image.jpg")
    sys.exit(1)

IMAGE_PATH = sys.argv[1]

# Load model
model = YOLO(MODEL_PATH)

# Load image
frame = cv2.imread(IMAGE_PATH)
if frame is None:
    print(f"❌ Failed to load image at: {IMAGE_PATH}")
    sys.exit(1)

# Run detection
results = model(IMAGE_PATH, conf=0.1, imgsz=640)

found_defects = False
for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        defect_type = model.names[cls_id]
        timestamp = format_timestamp()
        length_m = 0.0  # N/A for still images

        defect_filename = generate_defect_filename(SHEET_ID, defect_type)
        image_path = os.path.join("reports", SHEET_ID, "images", defect_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        save_image(frame, image_path)

        insert_defect(SHEET_ID, defect_type, length_m, image_path)

        print(f"✅ Detected: {defect_type} | Confidence: {conf:.2f} | Saved: {image_path}")
        found_defects = True

# Display result
annotated_frame = results[0].plot()
cv2.imshow("Test Image Detection", annotated_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

if not found_defects:
    print("⚠️ No defects detected.")

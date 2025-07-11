import os
import sys
from datetime import datetime
import cv2
import subprocess

# ------------------------------------------------------------------
COLLECTED_DIR = "data_collection/collected"
ANNOTATOR_SCRIPT = "data_collection/annotations/data_labeler.py"
# ------------------------------------------------------------------


def capture_images(defect_type: str):
    folder = os.path.join(COLLECTED_DIR, defect_type)
    os.makedirs(folder, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    counter = len([f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.png'))])
    print(f"📷  Capturing for '{defect_type}'.  SPACE=capture  ESC=quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Camera failure.")
            break

        cv2.imshow("Capture Window (SPACE save / ESC exit)", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:   # ESC
            break
        elif key == 32:  # SPACE
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"{defect_type}_{ts}_{counter}.jpg"
            save_path = os.path.join(folder, fname)
            cv2.imwrite(save_path, frame)
            print(f"✅ Saved {save_path}")
            counter += 1

    cap.release()
    cv2.destroyAllWindows()

    # Prompt for immediate annotation
    if counter and input("🖍️  Annotate now? [y/N]: ").strip().lower() == "y":
        launch_annotator(folder, class_id)


def launch_annotator(folder_path: str, class_id: int = 0):
    """Open data_labeler.py for each image in folder_path."""
    if not os.path.isfile(ANNOTATOR_SCRIPT):
        print(f"❌ Annotator not found at {ANNOTATOR_SCRIPT}")
        return

    imgs = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png'))]
    if not imgs:
        print("No images to annotate.")
        return

    print("🖍️  Launching annotation tool for each image…")
    for img in imgs:
        img_path = os.path.join(folder_path, img)
        subprocess.call([sys.executable, ANNOTATOR_SCRIPT, img_path, str(class_id)])


# ------------------------------------------------------------------
if __name__ == "__main__":
    # argv[1] = defect name  (required)
    # argv[2] = class id     (optional)
    if len(sys.argv) < 2:
        print("Usage:  python data_capture.py <defect_name> [class_id]")
        sys.exit(0)

    defect = sys.argv[1].replace(" ", "_")
    class_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    capture_images(defect)

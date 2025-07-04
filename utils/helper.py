# utils/helper.py

import os
from datetime import datetime
import cv2

def format_timestamp():
    """Return current timestamp in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")

def generate_defect_filename(sheet_id, defect_type):
    """Generate a unique image filename for a defect."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{sheet_id}_{defect_type}_{timestamp}.jpg"

def save_image(frame, path):
    """Save the current frame to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, frame)

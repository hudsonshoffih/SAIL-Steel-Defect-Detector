# train_gui_module.py

from tkinter import filedialog, messagebox, simpledialog
import shutil
import os
import subprocess

# Optional: use config constants
DATASET_DIR = "dataset/train"
IMG_DIR = os.path.join(DATASET_DIR, "images")
LBL_DIR = os.path.join(DATASET_DIR, "labels")

def train_from_gui():
    files = filedialog.askopenfilenames(
        title="Select defect images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if not files:
        messagebox.showinfo("❌ Cancelled", "No image files selected.")
        return

    label = simpledialog.askstring("Label", "Enter defect class label (e.g., Parity):")
    if not label:
        messagebox.showerror("⚠️ Missing Input", "You must enter a defect label.")
        return

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(LBL_DIR, exist_ok=True)

    for file in files:
        filename = os.path.basename(file)
        img_dest = os.path.join(IMG_DIR, filename)
        lbl_dest = os.path.join(LBL_DIR, filename.rsplit('.', 1)[0] + ".txt")

        shutil.copy(file, img_dest)

        # If label file doesn't exist, create an empty one
        if not os.path.exists(lbl_dest):
            with open(lbl_dest, 'w') as f:
                pass

    messagebox.showinfo("✅ Uploaded", f"{len(files)} images uploaded under label: {label}")

    # Call YOLO training
    messagebox.showinfo("📦 Training", "Starting training process...")
    result = subprocess.run(["python", "train_module.py"])

    if result.returncode == 0:
        messagebox.showinfo("✅ Training Complete", "Model retrained successfully.")
    else:
        messagebox.showerror("❌ Error", "Training process failed. Check console logs.")

# train_gui_module.py
from tkinter import filedialog, messagebox
import shutil
import os
import subprocess

def train_from_gui():
    files = filedialog.askopenfilenames(title="Select defect images")
    if not files:
        messagebox.showinfo("Cancelled", "No files selected.")
        return

    label = filedialog.askstring("Label", "Enter defect class label (e.g. Parity):")
    if not label:
        messagebox.showerror("Missing", "Label required.")
        return

    # Save to dataset/train/images/ and create empty labels if needed
    save_dir = f"dataset/train/images"
    os.makedirs(save_dir, exist_ok=True)
    for file in files:
        shutil.copy(file, save_dir)

    messagebox.showinfo("Uploading", "Files uploaded! Starting training...")

    # Call training subprocess
    subprocess.run(["python", "train_module.py"])
    messagebox.showinfo("✅ Training Complete", "Model retrained successfully.")

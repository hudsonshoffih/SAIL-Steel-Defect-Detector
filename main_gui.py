# main_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
import subprocess

from report_generator import generate_report
from live_detection import run_live_detection
from train_gui_module import train_from_gui
from data_collection_ui import launch_data_collection_ui  # ✅ new import

class SteelInspectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛠️ Steel Defect Inspection Dashboard")
        self.root.geometry("500x500")
        self.sheet_id = tk.StringVar()
        self.status = tk.StringVar(value="Status: Waiting...")
        self.defect_data = []

        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Enter Sheet Number:", font=("Arial", 12)).pack(pady=10)
        tk.Entry(self.root, textvariable=self.sheet_id, font=("Arial", 12)).pack()

        tk.Button(self.root, text="▶️ Start Inspection", command=self.start_inspection, bg="green", fg="white").pack(pady=10)
        tk.Button(self.root, text="⏹ End & Generate Report", command=self.end_inspection, bg="red", fg="white").pack(pady=5)
        tk.Button(self.root, text="📤 Train New Defect", command=self.train_gui, bg="blue", fg="white").pack(pady=10)

        # ✅ New button for data collection interface
        tk.Button(self.root, text="📸 Data Collection & Labeling", command=self.open_data_collection_ui, bg="orange", fg="black").pack(pady=10)

        tk.Label(self.root, textvariable=self.status, font=("Arial", 10)).pack(pady=20)

    def start_inspection(self):
        sid = self.sheet_id.get().strip()
        if not sid:
            messagebox.showerror("Error", "Please enter a Sheet Number")
            return

        self.status.set("🔍 Detecting... Press 'End' to finish.")
        self.defect_data = []

        def run_detection_thread():
            self.defect_data = run_live_detection(sheet_id=sid)

        threading.Thread(target=run_detection_thread).start()

    def end_inspection(self):
        if not self.defect_data:
            messagebox.showinfo("Info", "No defect data recorded.")
            return

        path = generate_report(self.sheet_id.get(), self.defect_data)
        self.status.set(f"✅ Report saved at: {path}")
        messagebox.showinfo("Success", f"Report generated for Sheet {self.sheet_id.get()}")

    def train_gui(self):
        train_from_gui()

    def open_data_collection_ui(self):
        # ✅ launch the PyQt5-based data collection interface
        launch_data_collection_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = SteelInspectorApp(root)
    root.mainloop()

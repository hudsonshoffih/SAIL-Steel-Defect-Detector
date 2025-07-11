import sys
import shutil
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QLineEdit, QTabWidget, QFileDialog, QMessageBox
)

from live_detection import run_live_detection
from report_generator import generate_report
from utils.sql_connector import init_db
from data_collection.data_collection import DataCollectionWidget  # Data‑collection tab

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steel Sheet Defect Inspection Dashboard")
        self.resize(650, 450)

        init_db()
        self.stop_flag = False
        self.detect_thread = None
        self.defects = []

        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_detection_tab(), "Detection")
        self.tabs.addTab(self.build_training_tab(), "Train")
        self.tabs.addTab(self.build_report_tab(), "Reports")
        self.tabs.addTab(DataCollectionWidget(), "Data Collection")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    # ---------------- Detection TAB ----------------
    def build_detection_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)

        self.sheet_id_input = QLineEdit(placeholderText="Enter Sheet Number…")
        lay.addWidget(self.sheet_id_input)

        self.start_btn = QPushButton("Start Detection")
        self.stop_btn  = QPushButton("🛑 Stop Detection")
        self.status_lbl = QLabel("Status: Idle")

        lay.addWidget(self.start_btn)
        lay.addWidget(self.stop_btn)
        lay.addWidget(self.status_lbl)

        self.start_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)
        return tab

    def detection_worker(self, sheet_id):
        """Background thread that runs detection."""
        self.defects = run_live_detection(
            sheet_id,
            stop_callback=lambda: self.stop_flag,
            show_alert_callback=self.show_defect_alert
        )
        # After loop ends generate report
        if self.defects:
            path = generate_report(sheet_id, self.defects)
            self.status_lbl.setText(f"✅ Report saved → {path}")
            QMessageBox.information(self, "Done", f"Report generated for {sheet_id}")
        else:
            self.status_lbl.setText("No defects recorded.")
        self.detect_thread = None   # thread finished

    def start_detection(self):
        sheet_id = self.sheet_id_input.text().strip()
        if not sheet_id:
            QMessageBox.warning(self, "Missing Sheet ID", "Please enter a sheet number.")
            return
        if self.detect_thread:  # Already running
            QMessageBox.information(self, "Running", "Detection already in progress.")
            return

        self.stop_flag = False
        self.status_lbl.setText("🔍 Detecting… Press Stop to finish.")
        # Launch background thread
        self.detect_thread = threading.Thread(target=self.detection_worker, args=(sheet_id,), daemon=True)
        self.detect_thread.start()

    def stop_detection(self):
        if not self.detect_thread:
            return
        self.stop_flag = True
        self.status_lbl.setText("Stopping… please wait.")

    def show_defect_alert(self, info):
        alert = QMessageBox()
        alert.setWindowTitle("⚠️ Defect Detected")
        alert.setText(f"{info['defect_type']} at {info['length_m']:.2f} m")
        alert.exec_()

    # ---------------- Training TAB ----------------
    def build_training_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)

        self.upload_btn = QPushButton("📤 Upload Images for Training")
        self.train_btn  = QPushButton("Train Model")

        lay.addWidget(self.upload_btn)
        lay.addWidget(self.train_btn)

        self.upload_btn.clicked.connect(self.upload_images)
        self.train_btn.clicked.connect(self.train_model)
        return tab

    def upload_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        if not paths:
            return
        dest_dir = "custom_data/train/images"
        os.makedirs(dest_dir, exist_ok=True)
        for p in paths:
            shutil.copy(p, os.path.join(dest_dir, os.path.basename(p)))
        QMessageBox.information(self, "Uploaded", f"{len(paths)} image(s) copied to training set.")

    def train_model(self):
        import subprocess
        ret = subprocess.run([sys.executable, "train_module.py"]).returncode
        if ret == 0:
            QMessageBox.information(self, "Training", "Model training completed!")
        else:
            QMessageBox.critical(self, "Training", "Training failed — check console.")

    # ---------------- Reports TAB ----------------
    def build_report_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        open_btn = QPushButton("📂 Open Reports Folder")
        lay.addWidget(open_btn)
        open_btn.clicked.connect(self.open_reports_folder)
        return tab

    def open_reports_folder(self):
        import subprocess, platform
        path = os.path.abspath("reports")
        if platform.system() == "Darwin":
            subprocess.call(["open", path])
        elif platform.system() == "Windows":
            subprocess.call(["explorer", path])
        else:
            subprocess.call(["xdg-open", path])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

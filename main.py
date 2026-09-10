import sys
import shutil
import os
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QLineEdit, QTabWidget, QFileDialog, QMessageBox
)

from live_detection import run_live_detection
from report_generator import generate_report
from utils.sql_connector import init_db
from data_collection.data_collection import DataCollectionWidget  # Data‑collection tab

class DetectionThread(QThread):
    defect_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(list, str)
    frame_signal = pyqtSignal(QImage)

    def __init__(self, sheet_id):
        super().__init__()
        self.sheet_id = sheet_id
        self.stop_flag = False

    def run(self):
        defects = run_live_detection(
            self.sheet_id,
            stop_callback=lambda: self.stop_flag,
            show_alert_callback=self.emit_defect,
            frame_callback=self.emit_frame
        )
        self.finished_signal.emit(defects, self.sheet_id)

    def emit_defect(self, info):
        self.defect_signal.emit(info)

    def emit_frame(self, qimg):
        self.frame_signal.emit(qimg)

    def stop(self):
        self.stop_flag = True

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steel Sheet Defect Inspection Dashboard")
        self.resize(700, 550)

        init_db()
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

        self.video_preview = QLabel("📷 Live Detection Stream (Click 'Start Detection')")
        self.video_preview.setAlignment(Qt.AlignCenter)
        self.video_preview.setFixedHeight(300)
        self.video_preview.setStyleSheet("background-color: #1e1e1e; color: #aaa; font-weight: bold; border-radius: 6px;")
        lay.addWidget(self.video_preview)

        self.start_btn = QPushButton("Start Detection")
        self.stop_btn  = QPushButton("🛑 Stop Detection")
        self.status_lbl = QLabel("Status: Idle")

        lay.addWidget(self.start_btn)
        lay.addWidget(self.stop_btn)
        lay.addWidget(self.status_lbl)

        self.start_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)
        return tab

    def start_detection(self):
        sheet_id = self.sheet_id_input.text().strip()
        if not sheet_id:
            QMessageBox.warning(self, "Missing Sheet ID", "Please enter a sheet number.")
            return
        if self.detect_thread and self.detect_thread.isRunning():
            QMessageBox.information(self, "Running", "Detection already in progress.")
            return

        self.status_lbl.setText("🔍 Detecting… Press Stop to finish.")
        self.detect_thread = DetectionThread(sheet_id)
        self.detect_thread.defect_signal.connect(self.show_defect_alert)
        self.detect_thread.finished_signal.connect(self.on_detection_finished)
        self.detect_thread.frame_signal.connect(self.update_detection_frame)
        self.detect_thread.start()

    def update_detection_frame(self, qimg):
        self.video_preview.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                self.video_preview.width(),
                self.video_preview.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    def stop_detection(self):
        if not self.detect_thread or not self.detect_thread.isRunning():
            return
        self.detect_thread.stop()
        self.status_lbl.setText("Stopping… please wait.")

    def on_detection_finished(self, defects, sheet_id):
        self.defects = defects
        if self.defects:
            path = generate_report(sheet_id, self.defects)
            self.status_lbl.setText(f"✅ Report saved → {path}")
            QMessageBox.information(self, "Done", f"Report generated for {sheet_id}")
        else:
            self.status_lbl.setText("No defects recorded.")
        self.detect_thread = None

    def show_defect_alert(self, info):
        alert = QMessageBox(self)
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

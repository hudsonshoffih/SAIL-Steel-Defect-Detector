import os
import cv2
import shutil
import sys 
import subprocess
import threading
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QInputDialog, QFileDialog, QMessageBox
)

# Constant Paths for config.py
COLLECTED_DIR = "data_collection/collected"
LABELS_DIR    = "data_collection/labels"
ANNOTATOR     = "data_collection/annotations/data_labeler.py"



class DataCollectionWidget(QWidget):
    """Full camera‑capture + annotation UI."""

    # Qt signal to update frame in GUI thread
    _frame_signal = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Collection")
        self.setFocusPolicy(Qt.StrongFocus)


        # State
        self.cap = None
        self.running = False
        self.current_defect = None

        # Ui widgets
        self.video_lbl = QLabel("Camera preview")
        self.video_lbl.setAlignment(Qt.AlignCenter)
        self.video_lbl.setFixedHeight(300)

        self.defect_list = QListWidget()
        self.refresh_defect_folders()

        self.start_btn   = QPushButton("Start Camera")
        self.stop_btn    = QPushButton("🛑 Stop Camera")
        self.capture_btn = QPushButton("Capture (SPACE)")
        self.annotate_btn= QPushButton("🖍️ Annotate Selected Image(s)")
        self.new_defect_btn = QPushButton("➕ New Defect Folder")
        self.upload_btn  = QPushButton("Upload Images for Annotation")

        # Layouts
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.capture_btn)

        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel("Live Camera"))
        vbox.addWidget(self.video_lbl)
        vbox.addLayout(btn_row)
        vbox.addWidget(QLabel("Defect Folders"))
        vbox.addWidget(self.defect_list)

        action_row = QHBoxLayout()
        action_row.addWidget(self.new_defect_btn)
        action_row.addWidget(self.annotate_btn)
        action_row.addWidget(self.upload_btn)
        vbox.addLayout(action_row)

        # Signals
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.capture_btn.clicked.connect(self.capture_frame)
        self.new_defect_btn.clicked.connect(self.create_defect_folder)
        self.annotate_btn.clicked.connect(self.launch_annotator)
        self.upload_btn.clicked.connect(self.upload_images)
        self._frame_signal.connect(self.update_frame)

        # Timer key‑listener for SPACE capture
        self.space_timer = QTimer(self)
        self.space_timer.timeout.connect(self.check_spacebar)
        self.space_timer.start(50)
        
    # space to capture    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.capture_frame()
    # Camera Handling
    def start_camera(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "❌ Cannot open webcam.")
            return
        self.running = True
        threading.Thread(target=self.read_frames, daemon=True).start()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_lbl.clear()

    def read_frames(self):
        while self.running and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
            self._frame_signal.emit(qimg)

    def update_frame(self, qimg):
        self.video_lbl.setPixmap(QPixmap.fromImage(qimg).scaled(
            self.video_lbl.width(), self.video_lbl.height(), Qt.KeepAspectRatio))

    # Space to Capture
    def check_spacebar(self):
        if not self.running:
            return
      

    def capture_frame(self):
        if not (self.running and self.cap):
            return
        defect = self.get_selected_defect()
        if not defect:
            QMessageBox.warning(self, "No Folder", "Select or create a defect folder first.")
            return

        ret, frame = self.cap.read()
        if not ret:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{defect}_{ts}.jpg"
        save_path = os.path.join(COLLECTED_DIR, defect, fname)
        cv2.imwrite(save_path, frame)
        QMessageBox.information(self, "Saved", f"✅ Image saved to {save_path}")
        self.refresh_defect_folders(select=defect)

    # Detect Foldeers
    def refresh_defect_folders(self, select: str | None = None):
        os.makedirs(COLLECTED_DIR, exist_ok=True)
        self.defect_list.clear()
        for d in sorted(os.listdir(COLLECTED_DIR)):
            if os.path.isdir(os.path.join(COLLECTED_DIR, d)):
                self.defect_list.addItem(d)
        # auto‑select
        if select:
            items = self.defect_list.findItems(select, Qt.MatchExactly)
            if items:
                self.defect_list.setCurrentItem(items[0])

    def create_defect_folder(self):
        name, ok = QInputDialog.getText(self, "New Defect", "Enter defect folder name:")
        if ok and name.strip():
            folder = os.path.join(COLLECTED_DIR, name.strip().replace(" ", "_"))
            os.makedirs(folder, exist_ok=True)
            self.refresh_defect_folders(select=name.strip())

    def get_selected_defect(self):
        item = self.defect_list.currentItem()
        return item.text() if item else None

      # Annotation
    def launch_annotator(self):
        defect = self.get_selected_defect()
        if not defect:
            QMessageBox.warning(self, "Select Folder", "Choose a defect folder first.")
            return

        folder_path = os.path.join(COLLECTED_DIR, defect)
        files, _ = QFileDialog.getOpenFileNames(self, "Select image(s) to annotate",
                                                folder_path, "Images (*.jpg *.jpeg *.png)")
        if not files:
            return

        for img_path in files:
            try:
                subprocess.Popen([sys.executable, ANNOTATOR, img_path, "0"])  # Default class_id = 0
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Cannot launch annotator:\n{exc}")

    # Upload Images
    def upload_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "",
                                                "Images (*.jpg *.jpeg *.png)")
        if not files:
            return
        defect = self.get_selected_defect()
        if not defect:
            QMessageBox.warning(self, "Select Folder", "Choose a defect folder to store images.")
            return

        dest_dir = os.path.join(COLLECTED_DIR, defect)
        os.makedirs(dest_dir, exist_ok=True)
        for f in files:
            shutil.copy(f, os.path.join(dest_dir, os.path.basename(f)))
        QMessageBox.information(self, "Uploaded", f"{len(files)} files copied to {dest_dir}")

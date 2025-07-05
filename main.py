import sys
import shutil
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QPushButton, QLineEdit, QTabWidget, QFileDialog, QMessageBox
)

from live_detection import run_live_detection
from report_generator import generate_report
from utils.sql_connector import init_db

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steel Sheet Defect Inspector 🛠️")
        self.resize(500, 300)

        init_db()  # Ensure DB is ready
        self.stop_flag = False  # ✅ Flag to stop detection

        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_detection_tab(), "Detection")
        self.tabs.addTab(self.build_training_tab(), "Train New Defect")
        self.tabs.addTab(self.build_report_tab(), "View Reports")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def build_detection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.sheet_id_input = QLineEdit()
        self.sheet_id_input.setPlaceholderText("Enter Sheet Number...")
        layout.addWidget(self.sheet_id_input)

        self.start_btn = QPushButton("Start Detection")
        self.stop_btn = QPushButton("Stop Detection")
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.start_btn.clicked.connect(self.handle_start_detection)
        self.stop_btn.clicked.connect(self.handle_stop_detection)

        tab.setLayout(layout)
        return tab

    def build_training_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.upload_btn = QPushButton("Upload New Defect Images")
        self.train_btn = QPushButton("Train Model")
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.train_btn)

        self.upload_btn.clicked.connect(self.handle_upload_images)
        self.train_btn.clicked.connect(self.handle_train_model)

        tab.setLayout(layout)
        return tab

    def build_report_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.open_folder_btn = QPushButton("Open Report Folder")
        layout.addWidget(self.open_folder_btn)
        self.open_folder_btn.clicked.connect(self.open_report_folder)

        tab.setLayout(layout)
        return tab

    def handle_start_detection(self):
        sheet_id = self.sheet_id_input.text().strip()
        if not sheet_id:
            QMessageBox.warning(self, "Missing Sheet ID", "❌ Please enter a sheet number.")
            return

        self.stop_flag = False  # ✅ Reset flag
        print(f"🚀 Starting detection for sheet: {sheet_id}")

        # Define callbacks
        def should_stop():
            return self.stop_flag

        def show_alert(defect_info):
            alert = QMessageBox()
            alert.setWindowTitle("⚠️ Defect Detected")
            alert.setText(
                f"🛑 {defect_info['defect_type']} detected at {defect_info['length_m']:.2f} meters!"
            )
            alert.exec_()

        defects = run_live_detection(
            sheet_id,
            stop_callback=should_stop,
            show_alert_callback=show_alert
        )

        print("📄 Generating report...")
        generate_report(sheet_id, defects)
        print("✅ Detection and report complete.")
        QMessageBox.information(self, "Success", "✅ Detection and report saved.")

    def handle_stop_detection(self):
        print("🛑 Stop signal sent.")
        self.stop_flag = True

    def handle_upload_images(self):
        img_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select New Defect Images", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not img_paths:
            return

        for img in img_paths:
            dest = "custom_data/train/images/" + os.path.basename(img)
            shutil.copy(img, dest)

        QMessageBox.information(self, "Uploaded", f"✅ Uploaded {len(img_paths)} images.")

    def handle_train_model(self):
        import subprocess
        result = subprocess.run([sys.executable, "train_module.py"])
        if result.returncode == 0:
            QMessageBox.information(self, "Model Trained", "✅ Model training complete!")
        else:
            QMessageBox.critical(self, "Training Error", "❌ Error during training.")

    def open_report_folder(self):
        import subprocess
        import platform
        path = os.path.abspath("reports")
        if platform.system() == "Darwin":
            subprocess.call(["open", path])
        elif platform.system() == "Windows":
            subprocess.call(["explorer", path])
        else:
            subprocess.call(["xdg-open", path])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

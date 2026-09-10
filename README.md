# 🛠️ Steel Sheet Defect Inspection System (`SAIL-Steel-Defect-Detector`)

An end-to-end, industrial-grade Computer Vision and Deep Learning solution for real-time steel surface defect detection, meter-based defective position tracking, automated database logging, and quality report generation.

---

## 📋 Executive Summary & Industrial Context

In modern steel manufacturing plants (such as continuous hot-rolling and cold-rolling mills), steel sheets move at high speeds along conveyor belts. Manual surface inspection by human operators is error-prone, hazardous, and incapable of capturing micro-defects at production speeds.

**The Solution:**
This project provides an automated, AI-driven quality inspection dashboard powered by **YOLOv8** and **PyQt5**. The system captures live video streams, detects structural surface anomalies (`Dent`, `Hole`, `Scratch`), computes the exact physical location (in meters) of each defect along the moving sheet, logs the findings into an SQLite database, and automatically outputs detailed Excel audit reports.

---

## 🏗️ System Architecture & Workflow

```text
 ┌────────────────┐      ┌─────────────────────────┐      ┌──────────────────────────┐
 │  Camera Feed   │ ───► │ OpenCV Preprocessing    │ ───► │ YOLOv8 AI Inference      │
 │ (Conveyor Line)│      │ (Frame Capture 640x640) │      │ (Detect: Dent/Hole/etc) │
 └────────────────┘      └─────────────────────────┘      └────────────┬─────────────┘
                                                                       │
 ┌────────────────┐      ┌─────────────────────────┐                   │ Detections
 │  PyQt5 GUI     │ ◄─── │ QThread Signal Dispatch │ ◄─────────────────┘ + Bounding Boxes
 │ (Live Stream)  │      │ (Frame & Alert Signals) │
 └────────────────┘      └────────────┬────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   Meter Tracker Engine   │ (Distance = Speed × Elapsed Time)
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │  SQLite Database & Excel │ (defects.db & reports/*.xlsx)
                         │     Report Generator     │
                         └──────────────────────────┘
```

### Detailed Execution Sequence:
1. **Video Acquisition**: The system grabs frames from the conveyor line camera feed using OpenCV.
2. **AI Inference**: Each frame is passed to a fine-tuned **YOLOv8** object detection model running on PyTorch.
3. **Defect Tracking**: When a defect is identified above the confidence threshold (`CONF_THRESHOLD = 0.4`), bounding boxes are rendered, and the elapsed conveyor time is converted to exact physical sheet length (in meters) by `MeterTracker`.
4. **Asynchronous Dispatch**: Frames and detection alerts are emitted via PyQt5 signals (`pyqtSignal`) from a worker thread (`QThread`) to update the GUI smoothly without freezing.
5. **Data Persistence & Audit**: Defect metadata (timestamp, meter position, defect class, confidence score, cropped image path) is stored in `defects.db` and formatted into an Excel report (`.xlsx`).

---

## 🔍 Module-by-Module Breakdown

| Module / Script | Description & Purpose | Key Technical Details |
| :--- | :--- | :--- |
| **`main.py`** | Primary PyQt5 Dashboard Application | Features 4 tabbed sections (**Detection**, **Train**, **Reports**, **Data Collection**). Uses `QThread` for thread-safe UI state updates. |
| **`live_detection.py`** | Core Real-time Vision Engine | Manages camera capture, runs YOLO inference loop, draws bounding boxes & meter overlays, and emits RGB frames. |
| **`utils/meter_tracker.py`** | Physical Distance Tracking | Tracks continuous sheet length in meters using formula $Length = Speed \times Time_{elapsed}$. |
| **`report_generator.py`** | Automated Report Exporter | Reads defect logs, formats Pandas DataFrames, exports `.xlsx` files, and saves cropped defect imagery under `reports/<Sheet_ID>/`. |
| **`utils/sql_connector.py`** | SQLite Database Interface | Initializes `defects.db` table schema and handles INSERT queries for defect event records. |
| **`data_collection/`** | Dataset Acquisition & Labeling | Contains tools to capture sample dataset images (`SPACE` key) and draw custom YOLO bounding box labels (`data_labeler.py`). |
| **`train_module.py`** | YOLO Model Trainer | Calls Ultralytics YOLO training API on `dataset/data.yaml` to retrain weights on new defect classes. |
| **`config.py`** | System Parameters Registry | Centralizes configuration constants (model paths, speed settings, confidence thresholds, database paths). |

---

## 🤖 Deep Learning & Model Specifications

- **Base Architecture**: Ultralytics YOLOv8 Nano (`yolov8n.pt`)
- **Target Classes**:
  1. `Dent` - Surface depression or impact mark.
  2. `Hole` - Puncture or physical perforation through the steel sheet.
  3. `Scratch` - Linear abrasion or surface scoring.
- **Input Resolution**: $640 \times 640$ pixels
- **Inference Speed**: ~32–38 ms per frame (~30 FPS) on standard CPU / GPU hardware.
- **Hyperparameters**:
  - Confidence Threshold: `0.40`
  - Training Epochs: `20`
  - Batch Size: `8` / `32`

---

## 📊 Database Schema

Metadata for every detected defect is persisted in SQLite (`defects.db`):

```sql
CREATE TABLE IF NOT EXISTS defect_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sheet_number TEXT NOT NULL,
    defect_type TEXT NOT NULL,
    length_meter REAL NOT NULL,
    timestamp TEXT NOT NULL,
    image_path TEXT NOT NULL
);
```

---

## 🎤 PPT Presentation Blueprint (Slide-by-Slide Guide)

Use the following slide outline to generate a presentation deck (PowerPoint / Google Slides):

### **Slide 1: Title Slide**
- **Title**: Steel Sheet Defect Inspection System
- **Subtitle**: AI-Powered Real-Time Quality Control & Defect Location Tracking
- **Presenter**: Project Team / Developer

### **Slide 2: Industry Problem Statement**
- Manual surface inspection in steel mills is slow, subjective, and dangerous.
- High-speed continuous manufacturing lines require automated, sub-second defect detection.
- Need for exact physical defect location tracking (meter offset) to trim defective steel sections accurately.

### **Slide 3: Proposed Solution & Core Features**
- **AI-Powered Object Detection**: YOLOv8 deep learning vision model.
- **Embedded Dashboard**: Integrated PyQt5 GUI stream running at ~30 FPS.
- **Defect Location Meter Tracking**: Calculates exact distance along the coil.
- **Automated Audit Reports**: SQLite persistence + Excel export with cropped images.

### **Slide 4: System Architecture**
- *Include the text flowchart from Section 2 above.*
- Highlight separation between camera acquisition, AI inference thread, PyQt GUI main thread, and database logging layer.

### **Slide 5: Computer Vision & Defect Classification**
- Classifies 3 primary defect types: **Dent**, **Hole**, **Scratch**.
- Model input size: 640x640 | Confidence threshold: 40%.
- Latency: ~35 ms per frame for real-time industrial operation.

### **Slide 6: Meter Tracking Logic**
- Real-time mathematical estimation:
  $$\text{Defect Position (m)} = \text{Conveyor Speed (m/s)} \times \text{Elapsed Time (s)}$$
- Allows quality assurance teams to pinpoint and remove flawed sections automatically.

### **Slide 7: Data Collection & Model Retraining Suite**
- Integrated dataset creation tool to capture new images via spacebar hotkey.
- Built-in annotation interface (`data_labeler.py`) for drawing bounding boxes and generating normalized YOLO labels (`class cx cy w h`).
- One-click retraining module (`train_module.py`) to adapt to new defect categories.

### **Slide 8: Automated Quality Reports**
- Displays sample Excel report layout (`reports/SHEET_101/SHEET_101.xlsx`).
- Columns included: `Defect Type`, `Timestamp`, `Length (m)`, `Defect Image Path`.

### **Slide 9: Technology Stack**
- **Programming Language**: Python 3.11
- **GUI Framework**: PyQt5
- **Vision & AI**: OpenCV, Ultralytics YOLOv8, PyTorch
- **Data Persistence**: SQLite3, Pandas, Openpyxl

### **Slide 10: Future Roadmap & Enhancements**
- Integration with hardware encoder/tachometer for exact physical pulse meter count.
- Multi-camera support (top and bottom sheet surface monitoring).
- Cloud sync for centralized plant-wide quality analytics.

---

## 🛠️ Environment Setup & Quick Run

```bash
# 1. Clone repository & setup environment
git clone https://github.com/hudsonshoffih/SAIL-Steel-Defect-Detector.git
cd Steel_Inspector

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch Dashboard
python main.py
```

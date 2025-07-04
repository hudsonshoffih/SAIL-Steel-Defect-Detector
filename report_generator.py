# report_generator.py

import os
import pandas as pd
from utils.sql_connector import insert_defect
from config import REPORT_DIR  # ✅ Use global path from config

def generate_report(sheet_id, defect_data):
    # Create report folder
    report_dir = os.path.join(REPORT_DIR, sheet_id)
    os.makedirs(report_dir, exist_ok=True)

    # Excel path
    excel_path = os.path.join(report_dir, f"{sheet_id}.xlsx")

    # Prepare DataFrame
    df = pd.DataFrame(defect_data)
    df = df[["defect_type", "timestamp", "length_m", "image_path"]]  # Keep columns in order
    df.rename(columns={
        "defect_type": "Defect Type",
        "timestamp": "Timestamp",
        "length_m": "Length (m)",
        "image_path": "Defect Image"
    }, inplace=True)

    # Save Excel file
    df.to_excel(excel_path, index=False)
    print(f"✅ Report saved: {excel_path}")

    # ✅ Insert into SQLite database for each defect
    for defect in defect_data:
        insert_defect(
            sheet_number=sheet_id,
            defect_type=defect["defect_type"],
            length_meter=defect["length_m"],
            image_path=defect["image_path"]
        )

    return excel_path

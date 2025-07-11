import sqlite3
from datetime import datetime
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS defect_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_number TEXT,
            defect_type TEXT,
            length_meter REAL,
            timestamp TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_defect(sheet_number, defect_type, length_meter, image_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO defect_logs (sheet_number, defect_type, length_meter, timestamp, image_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (sheet_number, defect_type, length_meter, timestamp, image_path))
    conn.commit()
    conn.close()
#use when neeed
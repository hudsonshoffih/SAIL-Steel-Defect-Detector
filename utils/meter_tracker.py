import time

class MeterTracker:
    def __init__(self, sheet_number, speed_m_per_sec=50.0):
        self.sheet_number = sheet_number
        self.speed = speed_m_per_sec  # meters per second
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.start_time = None

    def get_length(self):
        if self.start_time is None:
            return 0.0
        elapsed_time = time.time() - self.start_time
        return round(self.speed * elapsed_time, 2)  # meters rounded to 2 decimals
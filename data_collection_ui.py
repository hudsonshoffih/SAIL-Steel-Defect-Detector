# data_collection_ui.py

import sys
from PyQt5.QtWidgets import QApplication
from data_collection.data_collection import DataCollectionWidget

def launch_data_collection_ui():
    app = QApplication.instance()
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True
    widget = DataCollectionWidget()
    widget.resize(700, 600)
    widget.show()
    if created_app:
        app.exec_()

if __name__ == "__main__":
    launch_data_collection_ui()

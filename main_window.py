from PyQt5.QtWidgets import QMainWindow
from ui_main_window import ui_main_window


class MainWindow(QMainWindow):
    def __init__(self, data_file_path):
        super(MainWindow, self).__init__()
        self.ui = ui_main_window(data_file_path)
        self.ui.setup_ui(self)

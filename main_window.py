from PyQt5.QtWidgets import QMainWindow
from ui_main_window import ui_main_window


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = ui_main_window()
        self.ui.setup_ui(self)

from PyQt5.QtWidgets import QMainWindow
from ui_main_window import UIMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = UIMainWindow()
        self.ui.setup_ui(self)

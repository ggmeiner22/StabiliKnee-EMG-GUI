from PyQt5.QtWidgets import QMainWindow
from ui_main_window import ui_main_window


class MainWindow(QMainWindow):
    def __init__(self, csv_file, serial_port, baud_rate, num_sensors):
        super().__init__()
        self.ui = ui_main_window(csv_file, serial_port, baud_rate, num_sensors)
        self.ui.setup_ui(self)

    def closeEvent(self, event):
        # Stop the serial thread (and timer, if any) BEFORE the window is torn down
        self.ui.cleanup()
        super().closeEvent(event)

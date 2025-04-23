import warnings
warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D.*",
    module="matplotlib.projections"
)
import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from uMyo_serial_thread import get_new_filename

def main():
    subject = 'A00_Test123'
    csv_file = get_new_filename(subject)
    port = 'COM3'          # or '/dev/tty...' on Mac/Linux
    baud = 115200
    sensors = 4

    app = QApplication(sys.argv)
    window = MainWindow(csv_file, port, baud, sensors)
    window.show()
    sys.exit(app.exec_())


main()

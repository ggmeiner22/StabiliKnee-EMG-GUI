import warnings
warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D.*",
    module="matplotlib.projections"
)
import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from uMyoTest_2_25 import get_new_filename


color_red = "\u001b[31m"
color_magenta = "\u001b[35m"
color_reset = "\u001b[0m"


def main():
    subject = "A00_Test123"
    csv_file = get_new_filename(subject)
    print(f"{color_magenta}Using CSV file: {color_red}{csv_file}{color_reset}")

    app = QApplication(sys.argv)
    window = MainWindow(csv_file)
    window.show()
    sys.exit(app.exec_())


main()

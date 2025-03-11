import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow


def main():
    data_file_path = sys.argv[1]

    app = QApplication(sys.argv)
    window = MainWindow(data_file_path)
    window.show()
    sys.exit(app.exec_())


main()
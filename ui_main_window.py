import warnings

from PyQt5.QtWidgets import QInputDialog, QMessageBox

warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D.*",
    module="matplotlib.projections"
)
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from uMyo_serial_thread import SerialReaderFromUMyo

color_red = "\u001b[31m"
color_magenta = "\u001b[35m"
color_reset = "\u001b[0m"


class ui_main_window(object):
    def __init__(self, csv_file, serial_port, baud_rate, num_sensors):
        self.csv_file = csv_file
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.num_sensors = num_sensors
        self.timer_interval = 1000
        self.serial_thread = None
        self.timer = None
        self.is_existing_data = os.path.exists(csv_file) and os.path.getsize(csv_file) > 0

    def setup_ui(self, MainWindow):
        # Keep a reference to the parent widget
        self.main_window = MainWindow

        # Ask user for muscle group type (Quad or Hamstring)
        muscle_group = self.ask_for_muscle_group(self.main_window)
        self.muscle_group_labels = self.get_muscle_labels(muscle_group)

        # Set window dimensions
        MainWindow.resize(1800, 950)
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # Screen Title
        self.screen_title = QtWidgets.QLabel(self.centralwidget)
        self.screen_title.setGeometry(QtCore.QRect(715, 40, 361, 42))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.screen_title.sizePolicy().hasHeightForWidth())
        self.screen_title.setSizePolicy(sizePolicy)
        self.screen_title.setBaseSize(QtCore.QSize(7, 0))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.screen_title.setFont(font)
        self.screen_title.setObjectName("screen_title")

        # Horizontal line
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(70, 70, 1660, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        # Muscle header labels and other interface elements …
        # (The following UI code remains unchanged. For brevity, only key elements are shown.)
        self.muscle_h1 = QtWidgets.QLabel(self.centralwidget)
        self.muscle_h1.setGeometry(QtCore.QRect(100, 115, 125, 30))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.muscle_h1.setFont(font)
        self.muscle_h1.setObjectName("muscle_h1")
        self.muscle_h2 = QtWidgets.QLabel(self.centralwidget)
        self.muscle_h2.setGeometry(QtCore.QRect(950, 115, 125, 30))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.muscle_h2.setFont(font)
        self.muscle_h2.setObjectName("muscle_h2")
        self.muscle_h3 = QtWidgets.QLabel(self.centralwidget)
        self.muscle_h3.setGeometry(QtCore.QRect(100, 542, 125, 30))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.muscle_h3.setFont(font)
        self.muscle_h3.setObjectName("muscle_h3")
        self.muscle_h4 = QtWidgets.QLabel(self.centralwidget)
        self.muscle_h4.setGeometry(QtCore.QRect(950, 542, 125, 30))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.muscle_h4.setFont(font)
        self.muscle_h4.setObjectName("muscle_h4")
        MainWindow.setCentralWidget(self.centralwidget)

        # Layouts for labels and data boxes
        # (Layouts for a1, tma1, a2, tma2, etc. remain unchanged)
        self.verticalLayoutWidget_1 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_1.setGeometry(QtCore.QRect(300, 70, 251, 110))
        self.vtag_1 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_1)
        self.vtag_1.setContentsMargins(0, 0, 0, 0)
        self.a1_label = QtWidgets.QLabel(self.verticalLayoutWidget_1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.a1_label.setFont(font)
        self.vtag_1.addWidget(self.a1_label)
        self.tma1_label = QtWidgets.QLabel(self.verticalLayoutWidget_1)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tma1_label.setFont(font)
        self.tma1_label.setObjectName("tma1_label")
        self.vtag_1.addWidget(self.tma1_label)

        # (Other layouts for a2, tma2, a3, tma3, a4, tma4 are built similarly.)
        # …
        # Layout for box 1
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(500, 70, 121, 111))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.vdata_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.vdata_3.setContentsMargins(0, 0, 0, 0)
        self.vdata_3.setObjectName("vdata_3")
        self.a1 = QtWidgets.QLabel(self.verticalLayoutWidget_5)
        self.a1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.a1.setText("")
        self.a1.setObjectName("a1")
        self.vdata_3.addWidget(self.a1)
        self.tma1 = QtWidgets.QLabel(self.verticalLayoutWidget_5)
        self.tma1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tma1.setText("")
        self.tma1.setObjectName("tma1")
        self.vdata_3.addWidget(self.tma1)

        # Layout for label 2
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(1150, 70, 241, 111))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.vtag_11 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.vtag_11.setContentsMargins(0, 0, 0, 0)
        self.vtag_11.setObjectName("vtag_11")
        self.a2_label = QtWidgets.QLabel(self.verticalLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.a2_label.setFont(font)
        self.a2_label.setObjectName("a2_label")
        self.vtag_11.addWidget(self.a2_label)
        self.tma2_label = QtWidgets.QLabel(self.verticalLayoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tma2_label.setFont(font)
        self.tma2_label.setObjectName("tma2_label")
        self.vtag_11.addWidget(self.tma2_label)

        # Layout for box 2
        self.verticalLayoutWidget_6 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_6.setGeometry(QtCore.QRect(1350, 70, 121, 111))
        self.verticalLayoutWidget_6.setObjectName("verticalLayoutWidget_6")
        self.vdata2_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_6)
        self.vdata2_3.setContentsMargins(0, 0, 0, 0)
        self.vdata2_3.setObjectName("vdata2_3")
        self.a2 = QtWidgets.QLabel(self.verticalLayoutWidget_6)
        self.a2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.a2.setText("")
        self.a2.setObjectName("a2")
        self.vdata2_3.addWidget(self.a2)
        self.tma2 = QtWidgets.QLabel(self.verticalLayoutWidget_6)
        self.tma2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tma2.setText("")
        self.tma2.setObjectName("tma2")
        self.vdata2_3.addWidget(self.tma2)

        # Layout for label 3
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(300, 515, 251, 81))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_7")
        self.vtag_10 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.vtag_10.setContentsMargins(0, 0, 0, 0)
        self.vtag_10.setObjectName("vtag_10")
        self.a3_label = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.a3_label.setFont(font)
        self.a3_label.setObjectName("a3_label")
        self.vtag_10.addWidget(self.a3_label)
        self.tma3_label = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tma3_label.setFont(font)
        self.tma3_label.setObjectName("tma3_label")
        self.vtag_10.addWidget(self.tma3_label)

        # Layout for box 3
        self.verticalLayoutWidget_8 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_8.setGeometry(QtCore.QRect(500, 515, 121, 81))
        self.verticalLayoutWidget_8.setObjectName("verticalLayoutWidget_8")
        self.vdata3_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_8)
        self.vdata3_3.setContentsMargins(0, 0, 0, 0)
        self.vdata3_3.setObjectName("vdata3_3")
        self.a3 = QtWidgets.QLabel(self.verticalLayoutWidget_8)
        self.a3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.a3.setText("")
        self.a3.setObjectName("a3")
        self.vdata3_3.addWidget(self.a3)
        self.tma3 = QtWidgets.QLabel(self.verticalLayoutWidget_8)
        self.tma3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tma3.setText("")
        self.tma3.setObjectName("tma3")
        self.vdata3_3.addWidget(self.tma3)

        # Layout for label 4
        self.verticalLayoutWidget_9 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_9.setGeometry(QtCore.QRect(1150, 515, 241, 81))
        self.verticalLayoutWidget_9.setObjectName("verticalLayoutWidget_9")
        self.vtag_12 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_9)
        self.vtag_12.setContentsMargins(0, 0, 0, 0)
        self.vtag_12.setObjectName("vtag_12")
        self.a4_label = QtWidgets.QLabel(self.verticalLayoutWidget_9)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.a4_label.setFont(font)
        self.a4_label.setObjectName("a4_label")
        self.vtag_12.addWidget(self.a4_label)
        self.tma4_label = QtWidgets.QLabel(self.verticalLayoutWidget_9)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.tma4_label.setFont(font)
        self.tma4_label.setObjectName("tma4_label")
        self.vtag_12.addWidget(self.tma4_label)

        # Layout for box 4
        self.verticalLayoutWidget_10 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_10.setGeometry(QtCore.QRect(1350, 515, 121, 81))
        self.verticalLayoutWidget_10.setObjectName("verticalLayoutWidget_10")
        self.vdata4_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_10)
        self.vdata4_3.setContentsMargins(0, 0, 0, 0)
        self.vdata4_3.setObjectName("vdata4_3")
        self.a4 = QtWidgets.QLabel(self.verticalLayoutWidget_10)
        self.a4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.a4.setText("")
        self.a4.setObjectName("a4")
        self.vdata4_3.addWidget(self.a4)
        self.tma4 = QtWidgets.QLabel(self.verticalLayoutWidget_10)
        self.tma4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tma4.setText("")
        self.tma4.setObjectName("tma4")
        self.vdata4_3.addWidget(self.tma4)

        # Graph display widgets on QLabel
        self.graph_1 = QtWidgets.QLabel(self.centralwidget)
        self.graph_1.setGeometry(QtCore.QRect(10, 170, 850, 350))
        self.graph_1.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.graph_1.setText("")
        self.graph_1.setObjectName("graph_1")
        self.graph_2 = QtWidgets.QLabel(self.centralwidget)
        self.graph_2.setGeometry(QtCore.QRect(900, 170, 850, 350))
        self.graph_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.graph_2.setText("")
        self.graph_2.setObjectName("graph_2")
        self.graph_3 = QtWidgets.QLabel(self.centralwidget)
        self.graph_3.setGeometry(QtCore.QRect(10, 590, 850, 350))
        self.graph_3.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.graph_3.setText("")
        self.graph_3.setObjectName("graph_3")
        self.graph_4 = QtWidgets.QLabel(self.centralwidget)
        self.graph_4.setGeometry(QtCore.QRect(900, 590, 850, 350))
        self.graph_4.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.graph_4.setText("")
        self.graph_4.setObjectName("graph_4")

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Initialize CSV on first run
        if not self.is_existing_data:
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ['Timestamp'] +
                    [f"Muscle{i + 1} - {self.muscle_group_labels[i]}" for i in range(self.num_sensors)]
                )
        self.process_existing_data()

        # Start serial reader thread
        self.serial_thread = SerialReaderFromUMyo(
            self.csv_file,
            self.serial_port,
            self.baud_rate,
            self.num_sensors
        )
        self.serial_thread.data_received.connect(self.on_new_data)
        self.serial_thread.start()

    def on_new_data(self, elapsed, values):
        # New sample arrived; refresh UI
        self.update_data()

    def ask_for_muscle_group(self, parent):
        # Use the actual MainWindow as parent for dialogs
        options = ["Quad", "Hamstring"]
        choice, ok = QInputDialog.getItem(
            parent,
            "Select Muscle Group",
            "Choose muscle group:",
            options,
            0,
            False
        )
        if ok and choice:
            return choice
        else:
            QMessageBox.warning(
                parent,
                "Error",
                "No muscle group selected. Defaulting to Quad."
            )
            return "Quad"

    def get_muscle_labels(self, muscle_group):
        if muscle_group == "Quad":
            return ["RVL", "RVM", "LVM", "LVL"]
        elif muscle_group == "Hamstring":
            return ["RBF", "RST", "LST", "LBF"]
        else:
            return ["RVL", "RVM", "LVM", "LVL"]

    def retranslate_ui(self, MainWindow):

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "StabiliKnee EMG Readings"))
        self.a1_label.setText(_translate("MainWindow", "Max Amplitude :"))
        self.tma1_label.setText(_translate("MainWindow", "Total Muscle Activity :"))
        self.muscle_h1.setText(_translate("MainWindow", "Muscle #1"))
        self.a2_label.setText(_translate("MainWindow", "Max Amplitude :"))
        self.tma2_label.setText(_translate("MainWindow", "Total Muscle Activity :"))
        self.muscle_h2.setText(_translate("MainWindow", "Muscle #2"))
        self.a3_label.setText(_translate("MainWindow", "Max Amplitude :"))
        self.tma3_label.setText(_translate("MainWindow", "Total Muscle Activity :"))
        self.muscle_h3.setText(_translate("MainWindow", "Muscle #3"))
        self.a4_label.setText(_translate("MainWindow", "Max Amplitude :"))
        self.tma4_label.setText(_translate("MainWindow", "Total Muscle Activity :"))
        self.screen_title.setText(_translate("MainWindow", "StabiliKnee EMG Readings"))
        self.muscle_h4.setText(_translate("MainWindow", "Muscle #4"))
        # (Add other translations as needed)

    def update_data(self):
        # open once and count rows
        with open(self.csv_file) as f:
            rows = sum(1 for _ in f)
        # if only header, still run compute/show so you get zeros
        if rows <= 1:
            # optional: explicitly zero out labels/graphs
            self.compute_max_amplitude()
            self.compute_total_muscle_activity()
            self.show_graphs()
            return

        # otherwise run normally
        self.compute_max_amplitude()
        self.compute_total_muscle_activity()
        self.show_graphs()

    def process_existing_data(self):
        """Process and display historical CSV data."""
        self.compute_max_amplitude()
        self.compute_total_muscle_activity()
        self.show_graphs()

    def compute_max_amplitude(self):
        """Compute maximum amplitude per muscle from CSV data."""
        try:
            with open(self.csv_file, mode='r') as file:
                csvFile = csv.reader(file)
                next(csvFile)  # Skip header
                columns = [1, 2, 3, 4]
                max_values = {col: float('-inf') for col in columns}
                for row in csvFile:
                    for col in columns:
                        try:
                            value = float(row[col])
                            max_values[col] = max(max_values[col], value)
                        except (ValueError, IndexError):
                            pass
                for col in columns:
                    if max_values[col] == float('-inf'):
                        max_values[col] = 0
                # Update amplitude labels
                self.a1.setText(f"{max_values[1]:.2f} V")
                self.a2.setText(f"{max_values[2]:.2f} V")
                self.a3.setText(f"{max_values[3]:.2f} V")
                self.a4.setText(f"{max_values[4]:.2f} V")
                self.a1.setStyleSheet("font-size: 20px;")
                self.a2.setStyleSheet("font-size: 20px;")
                self.a3.setStyleSheet("font-size: 20px;")
                self.a4.setStyleSheet("font-size: 20px;")
            # (Add error handling or logging as needed)
        except Exception as e:
            print(f"{color_magenta}Error computing max amplitude: {color_red}{e}{color_reset}")

    def compute_total_muscle_activity(self):
        """Compute total muscle activity (integral) per muscle from CSV data."""
        try:
            with open(self.csv_file, mode='r') as file:
                csvFile = csv.reader(file)
                next(csvFile)  # Skip header
                time_vals = []
                columns = {1: [], 2: [], 3: [], 4: []}
                for row in csvFile:
                    # Convert values; fill missing with 0.0
                    row_data = [float(value) if value else 0.0 for value in row]
                    while len(row_data) < 5:
                        row_data.append(0.0)
                    time_vals.append(round(row_data[0], 3))
                    for col in range(1, 5):
                        columns[col].append(row_data[col] if col < len(row_data) else 0.0)
                time_arr = np.array(time_vals)
                integrals = {}
                for col, values in columns.items():
                    if len(time_arr) == len(values) and len(time_arr) > 1:
                        integrals[col] = np.trapz(values, time_arr)
                    else:
                        integrals[col] = 0.0
                # Update total muscle activity labels
                self.tma1.setText(f"{integrals[1]:.2f} mV")
                self.tma2.setText(f"{integrals[2]:.2f} mV")
                self.tma3.setText(f"{integrals[3]:.2f} mV")
                self.tma4.setText(f"{integrals[4]:.2f} mV")
                self.tma1.setStyleSheet("font-size: 20px;")
                self.tma2.setStyleSheet("font-size: 20px;")
                self.tma3.setStyleSheet("font-size: 20px;")
                self.tma4.setStyleSheet("font-size: 20px;")
        except Exception as e:
            print(f"{color_magenta}Error computing total muscle activity: {color_red}{e}{color_reset}")

    def show_graphs(self):
        """Read CSV data and update the graphs displayed on QLabel widgets."""
        try:
            with open(self.csv_file, mode='r') as file:
                csvFile = csv.reader(file)
                next(csvFile)  # Skip header
                time_vals = []
                columns = {1: [], 2: [], 3: [], 4: []}
                for row in csvFile:
                    row_data = [float(value) if value else 0.0 for value in row]
                    while len(row_data) < 5:
                        row_data.append(0.0)
                    time_vals.append(round(row_data[0], 3))
                    for col in range(1, 5):
                        columns[col].append(row_data[col] if col < len(row_data) else 0.0)
                # Plot graphs for each muscle and update the corresponding QLabel.
                self.plot_graph(columns[1], time_vals, self.graph_1)
                self.plot_graph(columns[2], time_vals, self.graph_2)
                self.plot_graph(columns[3], time_vals, self.graph_3)
                self.plot_graph(columns[4], time_vals, self.graph_4)
        except Exception as e:
            print(f"{color_magenta} displaying graphs: {color_red}{e}{color_reset}")

    def plot_graph(self, data, time_vals, graph_label):
        """Plot a matplotlib graph and set it as the pixmap of a QLabel."""
        fig, ax = plt.subplots(figsize=(9, 2.7))
        ax.plot(time_vals, data)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude (mV)')
        ax.set_title('Muscle Activity Over Time')
        canvas = FigureCanvas(fig)
        buf = BytesIO()
        canvas.print_png(buf)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        graph_label.setPixmap(pixmap)
        plt.close(fig)

    def cleanup(self):
        """Stop timer (if any) and serial thread during exit."""
        if self.timer is not None:
            self.timer.stop()

        if self.serial_thread is not None:
            try:
                # Stops the thread loop; don't call wait() here or the C++ object may already be gone
                self.serial_thread.stop()
            except RuntimeError:
                # If the thread object has already been deleted, just ignore
                pass

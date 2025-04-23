import sys
import time
import serial
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QInputDialog, QMessageBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def get_new_filename(subject="A0"):
    return f"TestSubject_{subject}.csv"


class LivePlotWidget(QWidget):
    def __init__(self, num_sensors, subject, muscle_group_labels):
        super().__init__()
        self.setWindowTitle("Real-time Sensor Data")

        self.num_sensors = num_sensors
        self.subject = subject  # Store subject for file naming
        self.muscle_group_labels = muscle_group_labels  # Store muscle group labels
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.time_window = 30  # 30 seconds of data
        self.time_data = deque(maxlen=300)
        self.sensor_data = [deque(maxlen=300) for _ in range(num_sensors)]

        self.start_time = time.time()
        self.lines = [self.ax.plot([], [], label=f"Sensor {i+1} - {self.muscle_group_labels[i]}")[0] for i in range(num_sensors)]

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Sensor Value")
        self.ax.set_title(f"Real-Time Sensor Data - {self.subject}")
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(0, 1000)  # Adjustable range
        self.ax.legend()

        # Create CSV file
        self.csv_filename = get_new_filename(self.subject)
        self.csv_file = open(self.csv_filename, mode='a', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Time (s)"] + [f"Sensor {i+1} - {self.muscle_group_labels[i]}" for i in range(num_sensors)])
        print(f"Recording data to {self.csv_filename}")

    def update_data(self, elapsed_time, sensor_values):
        self.time_data.append(elapsed_time)
        for i in range(self.num_sensors):
            self.sensor_data[i].append(sensor_values[i])
            self.lines[i].set_xdata(self.time_data)
            self.lines[i].set_ydata(self.sensor_data[i])

        # Auto-scale Y-axis with buffer
        min_val = min(min(sensor) for sensor in self.sensor_data if sensor)
        max_val = max(max(sensor) for sensor in self.sensor_data if sensor) + 10
        self.ax.set_ylim(min_val - 5, max_val)

        self.ax.set_xlim(max(0, elapsed_time - self.time_window), elapsed_time)
        self.canvas.draw()

        self.csv_writer.writerow([elapsed_time] + sensor_values)


class MainWindow(QMainWindow):
    def __init__(self, num_sensors=1, subject="A00_Test"):
        super().__init__()

        self.setWindowTitle("Sensor Data Plotter")
        self.setGeometry(100, 100, 800, 600)

        # Ask user for muscle group type (Quad or Hamstring)
        muscle_group = self.ask_for_muscle_group()
        self.muscle_group_labels = self.get_muscle_labels(muscle_group)

        self.widget = LivePlotWidget(num_sensors, subject, self.muscle_group_labels)
        self.setCentralWidget(self.widget)

        # Initialize serial communication
        self.serial_port = "/dev/cu.usbmodem744DBDA056282"  # Update with actual port
        self.baud_rate = 230400  # Increased baud rate

        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.05)
            time.sleep(2)  # Ensure connection stability
            print(f"Connected to {self.serial_port} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.ser = None

        self.start_time = time.time()

        if self.widget:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.read_serial_data)
            self.timer.start(30)  # Reduced delay from 50ms to 30ms

    def ask_for_muscle_group(self):
        # Ask user to select Quad or Hamstring
        options = ["Quad", "Hamstring"]
        choice, ok = QInputDialog.getItem(self, "Select Muscle Group", "Choose muscle group:", options, 0, False)
        if ok and choice:
            return choice
        else:
            QMessageBox.warning(self, "Error", "No muscle group selected. Defaulting to Quad.")
            return "Quad"  # Default if no choice is made

    def get_muscle_labels(self, muscle_group):
        # Define the muscle group labels
        if muscle_group == "Quad":
            return ["RVL", "RVM", "LVM", "LVL"]
        elif muscle_group == "Hamstring":
            return ["RBF", "RST", "LST", "LBF"]
        else:
            return ["RVL", "RVM", "LVM", "LVL"]  # Default to Quad if unknown


    def read_serial_data(self):
        if self.ser and self.ser.in_waiting > 0:
            try:
                raw_data = self.ser.read(self.ser.in_waiting).decode('utf-8')  # Read all available data
                lines = raw_data.split('\n')

                for raw_line in lines:
                    sensor_values = raw_line.strip().split()
                    if len(sensor_values) == self.widget.num_sensors:
                        sensor_values = list(map(float, sensor_values))
                        elapsed_time = time.time() - self.start_time
                        self.widget.update_data(elapsed_time, sensor_values)

            except ValueError:
                pass

    def closeEvent(self, event):
        if self.ser and self.ser.is_open:
            self.ser.close()
        if self.widget and hasattr(self.widget, 'csv_file'):
            self.widget.csv_file.close()
        print(f"Data saved to {self.widget.csv_filename if self.widget else 'Unknown file'}")
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(num_sensors=1, subject="B00_New")
    window.show()
    sys.exit(app.exec_())

# uMyoTest_2_25.py
import warnings
warnings.filterwarnings(
    "ignore",
    message="Unable to import Axes3D.*",
    module="matplotlib.projections"
)
import time
import serial
import csv
import os
from PyQt5.QtCore import QThread, pyqtSignal

color_red = "\u001b[31m"
color_magenta = "\u001b[35m"
color_reset = "\u001b[0m"


def get_new_filename(subject="A0"):
    """
    Return a CSV filename based on the subject identifier.
    e.g. get_new_filename("A00_Test123") → "TestSubject_A00_Test123.csv"
    """
    return f"TestSubject_{subject}.csv"


class SerialReaderFromUMyo(QThread):
    data_received = pyqtSignal()

    def __init__(self, csv_file, serial_port="COM3", baud_rate=9600, num_sensors=4, parent=None):
        super(SerialReaderFromUMyo, self).__init__(parent)
        self.csv_file = csv_file
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.num_sensors = num_sensors
        self._running = True
        self.ser = None

    def run(self):
        # Ensure the CSV file has a header if it does not already exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp'] + [f"Muscle{i}" for i in range(1, self.num_sensors + 1)])

        # Attempt to open the serial port
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"{color_magenta}Connected to serial port: {color_red}{self.serial_port}{color_magenta} at "
                  f"{color_red}{self.baud_rate}{color_magenta} baud.{color_reset}")
        except Exception as e:
            print(f"{color_magenta}Failed to connect to serial port: {color_red}{e}{color_reset}")
            return

        # Continuously read incoming data until stopped
        while self._running:
            try:
                if self.ser.in_waiting:
                    raw_line = self.ser.readline().decode('utf-8').strip()
                    if raw_line:
                        # Expect space-separated sensor values
                        sensor_values = raw_line.split()
                        if len(sensor_values) == self.num_sensors:
                            sensor_values = list(map(float, sensor_values))
                            timestamp = time.time()
                            # Append the new data row to the CSV file
                            with open(self.csv_file, 'a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow([timestamp] + sensor_values)
                                file.flush()
                            # Emit signal to notify UI of new data
                            self.data_received.emit()
            except Exception as e:
                print(f"{color_magenta}Error reading from serial: {color_red}{e}{color_reset}")

        # Clean up serial connection on exit
        if self.ser:
            self.ser.close()

    def stop(self):
        self._running = False

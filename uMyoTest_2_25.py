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

    def __init__(self, csv_file, serial_port, baud_rate, num_sensors, parent=None):
        super().__init__(parent)
        self.csv_file = csv_file
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.num_sensors = num_sensors
        self._running = False
        self.ser = None
        self.start_time = None

    def run(self):
        # Open serial port
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            time.sleep(2)
        except Exception as e:
            print(f"SerialReader: could not open port {self.serial_port}: {e}")
            return

        # Open CSV file for appending
        try:
            csvfile = open(self.csv_file, 'a', newline='')
            writer = csv.writer(csvfile)
        except Exception as e:
            print(f"SerialReader: could not open CSV file {self.csv_file}: {e}")
            if self.ser.is_open:
                self.ser.close()
            return

        self._running = True
        self.start_time = time.time()
        buffer = ""
        while self._running:
            try:
                if self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        parts = line.strip().split()
                        if len(parts) == self.num_sensors:
                            try:
                                values = [float(p) for p in parts]
                            except ValueError:
                                continue
                            elapsed = round(time.time() - self.start_time, 3)
                            # Write to CSV and flush
                            writer.writerow([elapsed] + values)
                            csvfile.flush()
                            # Notify UI to update
                            self.data_received.emit()
            except Exception as e:
                print(f"SerialReader error: {e}")
            time.sleep(0.03)

        # Clean up
        csvfile.close()
        if self.ser and self.ser.is_open:
            self.ser.close()

    def stop(self):
        self._running = False
        self.wait()

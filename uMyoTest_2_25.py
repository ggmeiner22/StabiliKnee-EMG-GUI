# uMyoTest_2_25.py
import time
import serial
import csv
from PyQt5.QtCore import QThread, pyqtSignal


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
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"Connected to serial port: {self.serial_port} at {self.baud_rate} baud.")
        except Exception as e:
            print("Failed to connect to serial port:", e)
            return

        while self._running:
            try:
                if self.ser.in_waiting:
                    raw_line = self.ser.readline().decode('utf-8').strip()
                    if raw_line:
                        # Assume Arduino sends space-separated sensor values (e.g., "123 456 789 101")
                        sensor_values = raw_line.split()
                        if len(sensor_values) == self.num_sensors:
                            sensor_values = list(map(float, sensor_values))
                            timestamp = time.time()
                            with open(self.csv_file, 'a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow([timestamp] + sensor_values)
                                file.flush()
                            self.data_received.emit()
            except Exception as e:
                print("Error reading from serial:", e)
        if self.ser:
            self.ser.close()

    def stop(self):
        self._running = False

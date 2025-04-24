import time
import serial
import csv
from PyQt5.QtCore import QThread, pyqtSignal

color_red = "\u001b[31m"
color_magenta = "\u001b[35m"
color_reset = "\u001b[0m"


def get_new_filename(subject="A0"):
    """Generate a new CSV filename based on subject ID."""
    return f"TestSubject_{subject}.csv"


class SerialReaderFromUMyo(QThread):
    # Emits elapsed timestamp and sensor values list
    data_received = pyqtSignal(float, list)

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
            print(f"{color_magenta}Could not open port {color_red}{self.serial_port}{color_magenta}:{color_reset} {e}\n")
            return

        # Prepare CSV file for appending data
        try:
            csvfile = open(self.csv_file, 'a', newline='')
            writer = csv.writer(csvfile)
        except Exception as e:
            print(f"{color_magenta}Could not open CSV {color_red}{self.csv_file}{color_magenta}:{color_reset} {e}\n")
            if self.ser and self.ser.is_open:
                self.ser.close()
            return

        self._running = True
        self.start_time = time.time()
        buffer = ""

        while self._running:
            try:
                if self.ser.in_waiting:
                    chunk = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                    buffer += chunk
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        parts = line.strip().split()
                        if len(parts) == self.num_sensors:
                            try:
                                vals = [float(p) for p in parts]
                            except ValueError:
                                continue
                            elapsed = round(time.time() - self.start_time, 3)
                            writer.writerow([elapsed] + vals)
                            csvfile.flush()
                            self.data_received.emit(elapsed, vals)
            except Exception as e:
                print(f"{color_magenta}Serial read error:{color_red} {e}{color_reset}\n")
            time.sleep(0.03)

        # Cleanup
        csvfile.close()
        if self.ser and self.ser.is_open:
            self.ser.close()

    def stop(self):
        """Stop the reading loop and close thread."""
        self._running = False
        self.wait()

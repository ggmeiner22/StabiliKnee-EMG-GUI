# StabiliKnee EMG Data Viewer

This repository contains a PyQt5 application for real-time acquisition, logging, and visualization of electromyography (EMG) sensor data from an Arduino.

## Features

- **Real-time data acquisition**: Background thread reads space-separated sensor values over serial.
- **CSV logging**: Automatic recording to `TestSubject_<ID>.csv` with header `Timestamp,Muscle1,Muscle2,Muscle3,Muscle4`.
- **Live metrics**: Computes and displays maximum amplitude and total muscle activity (integral) for each muscle.
- **Dynamic plotting**: Embedded matplotlib graphs in QLabel widgets, refreshing every second.
- **Clean shutdown**: Properly stops serial thread and closes file handles on exit.

## Prerequisites

- **Python**: 3.7 or higher
- **Arduino**: Device sending four space-separated values per line (e.g., `102 345 567 234`).
- **Python packages**:
  - PyQt5
  - pyserial
  - matplotlib
  - numpy

Install dependencies with:
```bash
pip install pyqt5 pyserial matplotlib numpy
```

## Configuration

1. **Serial Port & Baud Rate**
   - Default port: `COM3` (Windows) or `/dev/ttyUSB0` (Linux/Mac).
   - Default baud rate: `115200`.
   - To change, edit the instantiation in `main.py` or in `ui_main_window.py`:
     ```python
     from uMyoTest_2_25 import SerialReaderFromUMyo
     self.serial_thread = SerialReaderFromUMyo(
         csv_file, serial_port="<YOUR_PORT>", baud_rate=<YOUR_BAUD>
     )
     ```

2. **Subject ID & CSV Filename**
   - Default subject ID: `A00_Test123`.
   - CSV filename is generated via `get_new_filename(subject)` as `TestSubject_<subject>.csv`.
   - To override, change the `subject` variable in `main.py`:
     ```python
     from uMyoTest_2_25 import get_new_filename
     subject = "MySubject"
     csv_file = get_new_filename(subject)
     ```

## File Structure

```
├── main.py            # Entry point: sets up QApplication and MainWindow
├── main_window.py     # QMainWindow wrapper loading the UI
├── ui_main_window.py  # UI layout and update logic (labels, graphs, timers)
└── uMyoTest_2_25.py   # SerialReaderFromUMyo thread and CSV header helper
```

## Running the Application

From the project root directory, simply run:
```bash
python main.py
```

- **Console output** will confirm:
  - The CSV file in use (e.g., `TestSubject_A00_Test123.csv`).
  - Serial port connection status.
- **GUI window** will launch and begin updating metrics and plots in real time.

## Troubleshooting

- **No GUI data updates**:
  - Verify Arduino is sending data lines of exactly four space-separated values.
  - Check that the serial port name and baud rate match your device.
- **Permission errors on serial port (Linux/Mac)**:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
  or
  ```
  sudo chmod 0700 /run/user/$(id -u)
  ```
  then log out/in.
- **Missing Python packages**:
  ```bash
  pip install pyqt5 pyserial matplotlib numpy
  ```

## Contribution

Feel free to open issues or pull requests to:
- Add new metrics or visualizations.
- Enhance UI layout or styling.
- Support variable sensor counts.

---

*Enjoy real-time EMG visualization!*

Current interface visual:

![image](https://github.com/user-attachments/assets/4fd6d4ed-b456-4cc5-a122-ff0a05906c03)


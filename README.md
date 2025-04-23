# StabiliKnee EMG GUI

A PyQt5-based desktop application to visualize real-time EMG data streamed from an Arduino (using the uMyo BLE library). Data are logged to CSV and displayed as four muscle-activity graphs along with max amplitudes and total activity metrics.

---

## Features

- **Real-time plotting** of up to 4 EMG channels  
- **Max Amplitude** and **Total Muscle Activity** (integral) computed live  
- **CSV logging** for offline analysis  
- **Muscle group selection** (Quad vs Hamstring) at startup  
- **Clean shutdown** of serial reader thread  

---

## Requirements

- Python 3.7+  
- PyQt5  
- pyserial  
- numpy  
- matplotlib  
- Arduino IDE (to upload the `.ino` sketch)  

---

## Installation

1. Clone this repo:
   ```bash
   git clone https://your.repo.url/StabiliKnee-EMG-GUI.git
   cd StabiliKnee-EMG-GUI
2. Create a Python virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
3. Install Python dependencies:
   ```bash
   pip install PyQt5 pyserial numpy matplotlib
   
---

## Arduino Setup

1. Open `green_red_EMG_button.ino` in the Arduino IDE.  
2. Verify that `Serial.begin(115200);` is set.  
3. Compile & upload to your board (e.g. Arduino Nano 33 BLE).  
4. Plug in the board; note the COM/tty port (e.g. `COM3` or `/dev/cu.usbmodem…`).

## Python Application Usage

1. Edit `main.py` to set:
   ```python
   subject = "A00_Test123"
   port    = 'COM3'        # or '/dev/ttyUSB0'
   baud    = 115200
   sensors = 4
2. Run the app:
   ```bash
   python main.py
3. On launch, select Quad or Hamstring muscle grouping.
4. Watch live graphs, max amplitudes, and total activity update as EMG data arrive.

---

## File Structure

```
StabiliKnee-EMG-GUI/
├── green_red_EMG_button.ino    # Arduino sketch for EMG + LED/button
├── main.py                     # Application entry point
├── main_window.py              # QMainWindow wrapper
├── ui_main_window.py           # PyQt5 UI layout & logic
└── uMyo_serial_thread.py       # QThread to read serial, log CSV, emit data
```
---
## Troubleshooting

- **No GUI data updates**:
  - Verify Arduino is sending data lines of exactly four space-separated values.
  - Check that the serial port name and baud rate match your device.
- **Permission errors on serial port (Linux/Mac)**:
  ```bash
  $ sudo usermod -a -G dialout $USER
  ```
  or
  ```
  $ sudo chmod 0700 /run/user/$(id -u)
  ```
  then log out/in.
- **Missing Python packages**:
  ```bash
  $ pip install pyqt5 pyserial matplotlib numpy
  ```
---
## Current interface visual

![image](https://github.com/user-attachments/assets/4fd6d4ed-b456-4cc5-a122-ff0a05906c03)
---
*Enjoy real-time EMG visualization!*


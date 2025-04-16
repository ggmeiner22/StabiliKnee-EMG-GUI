#include <uMyo_BLE.h>

const int buttonPin = 12;     // Button connected to pin 12
const int greenLedPin = 10;  // Green LED for active state
const int redLedPin = 11;    // Red LED for inactive state
bool scriptRunning = false;  // Track if script is running
bool lastButtonState = HIGH; // tores previous button state

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);  // Use internal pull-up resistor
  pinMode(greenLedPin, OUTPUT);  // Green LED pin as output
  pinMode(redLedPin, OUTPUT);  // Red LED pin as output
  Serial.begin(115200);
  uMyo.begin();

  // Start with Red LED ON (inactive) and Green LED OFF
  digitalWrite(redLedPin, HIGH);
  digitalWrite(greenLedPin, LOW);
}

void loop() {
  int buttonState = digitalRead(buttonPin);  // Read button state

  // Detect button press (LOW means pressed)
  if (buttonState == LOW && lastButtonState == HIGH) {
    delay(50);  // Debounce delay
    scriptRunning = !scriptRunning;  // Toggle script state

    if (scriptRunning) {
      digitalWrite(greenLedPin, HIGH);  // Turn on Green LED
      digitalWrite(redLedPin, LOW);  // Turn off Red LED
      Serial.println("Button Pressed - Running uMyo Script");
    } else {
      digitalWrite(greenLedPin, LOW);  // Turn off Green LED
      digitalWrite(redLedPin, HIGH);  // Turn on Red LED
      Serial.println("Button Pressed - Stopping uMyo Script");
    }
  }
  lastButtonState = buttonState;  // Update last button state

  // Run the script only if scriptRunning is true
  if (scriptRunning) {
    uMyo.run();
    int dev_count = uMyo.getDeviceCount();  // Get device count

    for (int d = 0; d < dev_count; d++) {
      Serial.print(uMyo.getMuscleLevel(d));
      if (d < dev_count - 1) Serial.print(' ');
      else Serial.println();
    }
    delay(60);  // Small delay to prevent excessive data printing
  }
}

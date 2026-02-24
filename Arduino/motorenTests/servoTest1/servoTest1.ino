#include <Servo.h>

Servo meinServo; // Servo-Objekt erstellen

void setup() {
  meinServo.attach(8); // Pin 9 mit Servo verbinden
}

void loop() {
  meinServo.write(45);    // Servo auf 0°
  delay(1000);
  meinServo.write(90);   // Servo auf 90°
  delay(1000);
  meinServo.write(180);  // Servo auf 180°
  delay(1000);
}

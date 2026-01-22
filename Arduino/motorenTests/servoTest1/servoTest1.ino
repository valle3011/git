#include <Servo.h>

Servo meinServo; // Servo-Objekt erstellen

void setup() {
  meinServo.attach(4); // Pin 9 mit Servo verbinden
}

void loop() {
  meinServo.write(0);    // Servo auf 0°
  delay(1000);
  meinServo.write(90);   // Servo auf 90°
  delay(1000);
  meinServo.write(180);  // Servo auf 180°
  delay(1000);
}

#include <Servo.h>

Servo meinServo; // Servo-Objekt erstellen

void setup() {
  meinServo.attach(8); // Pin 9 mit Servo verbinden
}

void loop() {
  meinServo.write(180);
  delay(2000);
  meinServo.write(0);
  delay(2000);  


}

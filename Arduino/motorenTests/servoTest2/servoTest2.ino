#include <Servo.h>

Servo meinServo;       // Servo-Objekt erstellen
int potPin = A0;       // Pin, an dem das Potentiometer angeschlossen ist
int potWert;           // Variable für den gelesenen Wert

void setup() {
  meinServo.attach(9); // Pin 9 mit dem Servo verbinden
}

void loop() {
  potWert = analogRead(potPin);                  // Lese Potentiometerwert (0–1023)
  int servoWinkel = map(potWert, 0, 1023, 0, 180); // Mappe Wert auf 0–180°
  meinServo.write(servoWinkel);                 // Setze Servo auf den berechneten Winkel
  delay(15); // Kurze Pause, damit der Servo geschmeidig bewegt
}

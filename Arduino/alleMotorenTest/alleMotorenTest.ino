#include <Servo.h>

Servo meinServo; // Servo-Objekt erstellen

const int outPin = 9;     // PWM Pin zum ESC (D9)
const int pwmStop = 60;   // "kein Gas" (ggf. anpassen)
const int pwmLow  = 90;   // kleines Gas
const int pwmMed  = 120;  // mittleres Gas

const int rpwmPin = 5;   // PWM für "vorwärts"
const int lpwmPin = 6;   // PWM für "rückwärts"

void setup() {
  pinMode(outPin, OUTPUT);
  meinServo.attach(4); // Pin 9 mit Servo verbinden
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);
  // Falls R_EN/L_EN an Arduino: pinMode(enPin, OUTPUT); digitalWrite(enPin, HIGH);
  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);

  // Sicher starten: STOP
  analogWrite(outPin, pwmStop);
  delay(2000);
}

void loop() {
  // 1) kleines Gas
  analogWrite(outPin, pwmLow);
  delay(2000);

  // 2) mittleres Gas
  analogWrite(outPin, pwmMed);
  delay(2000);

  // 3) STOP

  meinServo.write(180);
  delay(2000);
  meinServo.write(0);
  delay(2000);  

  analogWrite(rpwmPin, 255);
  analogWrite(lpwmPin, 0);
  delay(8000);
  // Motor anhalten
  analogWrite(rpwmPin, 0);
  delay(3000);
  analogWrite(outPin, pwmStop);
  delay(3000);
}
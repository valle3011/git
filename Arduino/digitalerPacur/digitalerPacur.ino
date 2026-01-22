#include <Servo.h>

Servo bremse;
const int bremsePin = 4;

const int antribPin = 9;
const int rpwmPin = 5;
const int lpwmPin = 6;

void setup() {
  // put your setup code here, to run once:
  bremse.attach(bremsePin);
  bremse.write(0);

  pinMode(antribPin, OUTPUT);
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);

  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);

  analogWrite(antribPin, 60);
}

void loop() {
  // put your main code here, to run repeatedly:

}

void antribFahren(int speed) {
  analogWrite(antribPin, speed);
}

void bremseAn() {
  analogWrite(antribPin, 60);
  bremse.write(180);
}

void bremseAus() {
  bremse.write(0)
}

void lenkRechts() {
  static unsigned long startTime = 0;
  static bool aktiv = false;

  if (!aktiv) {
    analogWrite(rpwmPin, 255);
    analogWrite(lpwmPin, 0);
    Serial.println("Begin Rechts");
    startTime = millis();
    aktiv = true;
  }

  if (aktiv && millis() - startTime >= 800) {
    analogWrite(rpwmPin, 0);
    Serial.println("Ende Rechts");
    aktiv = false;
  }
}

void lenkLinks() {
  static unsigned long startTime = 0;
  static bool aktiv = false;

  if (!aktiv) {
    analogWrite(lpwmPin, 255);
    analogWrite(rpwmPin, 0);
    Serial.println("Begin Links");
    startTime = millis();
    aktiv = true;
  }

  if (aktiv && millis() - startTime >= 800) {
    analogWrite(lpwmPin, 0);
    Serial.println("Ende Links");
    aktiv = false;
  }
}
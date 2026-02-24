#include <Servo.h>

Servo bremse;
const int bremsePin = 4;

const int antribPin = 9;
const int rpwmPin = 5;
const int lpwmPin = 6;

int entscheidung = 0; // ABC

const int lenkPin = A0;
int potValue = 0;

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
  switch (entscheidung) {
    case 1:
      antribFahren();
      break;

    case 2:
      bremseAn();
      break;

    case 3:
      bremseAus();
      break;

    default:
      bremseAn();
      break;
  }

  int lenkValue = analogRead(lenkPin); // 455 mitte, nach rechts kleiner, nach links größer
  if () {

  } else if () {

  }
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

  if (aktiv && millis() - startTime >= 800) { //800 als Variable für dynamisches Lenken
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

  if (aktiv && millis() - startTime >= 800) { //800 als Variable für dynamisches Lenken
    analogWrite(lpwmPin, 0);
    Serial.println("Ende Links");
    aktiv = false;
  }
}
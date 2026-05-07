#include <Servo.h>
#include <SoftwareSerial.h>
#include <TinyGPS++.h>

Servo bremse;
const int bremsePin = 12;

const int antribPin = 9;

const int rpwmPin = 10;
const int lpwmPin = 11;
int richtung = 0; //-1 ist ganz links, 0 ist mitte, +1 ist rechts

int entscheidung = 0;

const int lenkPin = A0;
int potValue = 0;

TinyGPSPlus gps;

int TRIG_L = 3;
int ECHO_L = 4;
int TRIG_R = 5;
int ECHO_R = 6;
int TRIG_H = 7;
int ECHO_H = 8;

String cmd = "";

void setup() {
  // put your setup code here, to run once:
  bremse.attach(bremsePin);
  bremse.write(90);

  pinMode(antribPin, OUTPUT);
  
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);

  pinMode(TRIG_L, OUTPUT);
  pinMode(ECHO_L, INPUT);
  pinMode(TRIG_R, OUTPUT);
  pinMode(ECHO_R, INPUT);
  pinMode(TRIG_H, OUTPUT);
  pinMode(ECHO_H, INPUT);


  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);

  analogWrite(antribPin, 60);

  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(115200);

  delay(1500);
  Serial2.println("READY");
}

void loop() {
  // put your main code here, to run repeatedly:
  cmd = Serial2.read();
  switch (cmd) {
    case "FORWARD":
      antribFahren();
      break;

    case "STOP":
      bremseAn();
      break;

    default:
      bremseAn();
      break;
  }

  int lenkValue = analogRead(lenkPin);
  if (lenkValue >= 500 || cmd == "LEFT") {
    // Serial.println(richtung);
    // Serial.println(lenkValue);
    lenkLinks();
  }
  
  if (lenkValue <= 330 || cmd == "RIGHT") {
    // Serial.println(richtung);
    // Serial.println(lenkValue);
    lenkRechts();
  }

  ultraSennsor();

  gpsSennsor();
}

void antribFahren() {
  bremse.write(90)
  analogWrite(antribPin, 120);
}

void bremseAn() {
  analogWrite(antribPin, 60);
  bremse.write(180);
}

void lenkRechts() {
  if (richtung != 1) {
    static unsigned long startTime = 0;
    static bool aktiv = false;

    if (!aktiv) {
      analogWrite(rpwmPin, 255);
      analogWrite(lpwmPin, 0);
      // Serial.println("Begin Rechts");
      startTime = millis();
      aktiv = true;
    }

    if (aktiv && millis() - startTime >= 800) { //800 als Variable für dynamisches Lenken
      analogWrite(rpwmPin, 0);
      // Serial.println("Ende Rechts");
      Serial.println(millis());
      aktiv = false;
      richtung++;
    }
  }
}

void lenkLinks() {
  if (richtung != -1) {
    static unsigned long startTime = 0;
    static bool aktiv = false;

    if (!aktiv) {
      analogWrite(lpwmPin, 255);
      analogWrite(rpwmPin, 0);
      // Serial.println("Begin Links");
      startTime = millis();
      aktiv = true;
    }

    if (aktiv && millis() - startTime >= 800) { //800 als Variable für dynamisches Lenken
      analogWrite(lpwmPin, 0);
      // Serial.println("Ende Links");
      Serial.println(millis());
      aktiv = false;
      richtung--;
    }
  }
}

long messen(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long dauer = pulseIn(echoPin, HIGH, 30000); // max. 30 ms
  if (dauer == 0) return -1; // kein Echo
  return dauer * 0.034 / 2;
}

void ultraSennsor() {
  long links  = messen(TRIG_L, ECHO_L);
  long rechts = messen(TRIG_R, ECHO_R);
  long hinten = messen(TRIG_H, ECHO_H);

  Serial.println("-----------------------------");

  Serial.println(links);
  Serial.println(rechts);
  Serial.println(hinten);
}

void gpsSennsor() {
  while (Serial1.available()) {
    gps.encode(Serial1.read());
  }

  if (gps.location.isUpdated()) {

    Serial.println("-----------------------------");

    Serial.print("Breitengrad: ");
    Serial.println(gps.location.lat(), 6);

    Serial.print("Laengengrad: ");
    Serial.println(gps.location.lng(), 6);

    Serial.print(gps.speed.kmph()); 
    Serial.println(" km/h");

    Serial.print("Hoehe: ");
    Serial.print(gps.altitude.meters());
    Serial.println(" m");

    Serial.print("Satelliten: ");
    Serial.println(gps.satellites.value());
  }
}
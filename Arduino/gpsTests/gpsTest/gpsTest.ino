#include <SoftwareSerial.h>

SoftwareSerial gpsSerial(0, 1); // RX, TX

void setup() {
  Serial.begin(9600);     // USB → PC
  Serial1.begin(9600);   // GPS auf Pins 0/1
  Serial.println("GPS RAW TEST");
}

void loop() {
  while (Serial1.available()) {
    char c = Serial1.read();
    Serial.write(c); // direkt an den PC weiterleiten
  }
}
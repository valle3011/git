#include <SoftwareSerial.h>

SoftwareSerial gpsSerial(0, 1); // RXgps zu 1 und TXgps zu 0

#include <TinyGPS++.h>

TinyGPSPlus gps;

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
}

void loop() {
  while (Serial1.available()) {
    gps.encode(Serial1.read());
  }

  if (gps.location.isUpdated()) {
    Serial.print("Breitengrad: ");
    Serial.println(gps.location.lat(), 6);

    Serial.print("Laengengrad: ");
    Serial.println(gps.location.lng(), 6);

    Serial.print(gps.speed.kmph());  // km/h
    Serial.println(" km/h");

    Serial.print("Hoehe: ");
    Serial.print(gps.altitude.meters());
    Serial.println(" m");

    Serial.print("Satelliten: ");
    Serial.println(gps.satellites.value());

    Serial.println("------------------");
  }
}
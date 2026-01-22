#include <SoftwareSerial.h>

SoftwareSerial gpsSerial(0, 1); // RX, TX

void setup() {
  Serial.begin(9600);
  gpsSerial.begin(9600);
}

void loop() {
  while (gpsSerial.available()) {
    char c = gpsSerial.read();
    Serial.write(c); // Gibt die rohen GPS-Daten aus
  }
}

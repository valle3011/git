void setup() {
  Serial.begin(115200);  // USB oder Hardware-Serial
}

void loop() {
  if (Serial.available()) {
    String received = Serial.readString(); // oder readBytes()
    // hier die Distanzwerte verarbeiten
  }
}
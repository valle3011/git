void setup() {
  Serial.begin(115200);
  delay(2000);   // wichtig für Linux!
}

void loop() {
  Serial.println("Raspberry Pi <-> Arduino OK");
  delay(1000);
}
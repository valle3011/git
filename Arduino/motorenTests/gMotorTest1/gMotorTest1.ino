const int outPin = 9;     // PWM Pin zum ESC (D9)
const int pwmStop = 60;   // "kein Gas"
const int pwmLow  = 90;   // kleines Gas
const int pwmMed  = 180;  // mittleres Gas

void setup() {
  pinMode(outPin, OUTPUT);

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
  analogWrite(outPin, pwmStop);
  delay(3000);
}
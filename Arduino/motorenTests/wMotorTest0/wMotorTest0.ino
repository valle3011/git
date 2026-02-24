// Beispiel: DPS (D5 = RPWM, D6 = LPWM), R_EN & L_EN dauerhaft HIGH (5V)
const int rpwmPin = 2;   // PWM für "vorwärts"
const int lpwmPin = 3;   // PWM für "rückwärts"

void setup() {
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);
  // Falls R_EN/L_EN an Arduino: pinMode(enPin, OUTPUT); digitalWrite(enPin, HIGH);
  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);
}

void loop() {
  // Motor vorwärts mit steigender Geschwindigkeit
  analogWrite(rpwmPin, 255);
  analogWrite(lpwmPin, 0);
  delay(800);

  // Motor anhalten
  analogWrite(rpwmPin, 0);
  delay(3000);

  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 255);
  delay(800);

  analogWrite(lpwmPin, 0);
  delay(3000);
}

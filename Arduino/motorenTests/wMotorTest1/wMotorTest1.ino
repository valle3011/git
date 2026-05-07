int rpwmPin = 11;
int lpwmPin = 10;

int rEnPin = 7;
int lEnPin = 8;

void setup() {
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);
  pinMode(rEnPin, OUTPUT);
  pinMode(lEnPin, OUTPUT);

  // Beide Enable-Pins aktivieren
  digitalWrite(rEnPin, HIGH);
  digitalWrite(lEnPin, HIGH);
}

void loop() {
  // Vorwärts
  analogWrite(rpwmPin, 255);
  analogWrite(lpwmPin, 0);
  delay(2000);

  // Stop
  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);
  delay(1000);

  // Rückwärts
  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 255);
  delay(2000);

  // Stop
  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);
  delay(3000);
}
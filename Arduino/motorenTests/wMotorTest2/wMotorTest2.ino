// PWM-Pins für IBT-2
const int rpwmPin = 5;
const int lpwmPin = 6;

// Enable-Pins
const int rEnPin = 7;
const int lEnPin = 8;

// Potentiometer
const int potPin = A0;

void setup() {
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);
  pinMode(rEnPin, OUTPUT);
  pinMode(lEnPin, OUTPUT);

  // Anfangszustand: Motor aus
  digitalWrite(rEnPin, LOW);
  digitalWrite(lEnPin, LOW);
  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);
}

void loop() {
  // Lese Potentiometer (0–1023)
  int potValue = analogRead(potPin);

  // Skaliere auf PWM 0–255
  int pwmValue = map(potValue, 0, 1023, 0, 255);

  // Motor vorwärts steuern
  digitalWrite(rEnPin, HIGH);
  digitalWrite(lEnPin, LOW);
  analogWrite(rpwmPin, pwmValue);
  analogWrite(lpwmPin, 0);

  // Kleines Delay für Stabilität
  delay(10);
}

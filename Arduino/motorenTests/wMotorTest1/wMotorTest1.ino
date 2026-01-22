// Mit aktivem Schalten von R_EN und L_EN

// PWM-Pins
int rpwmPin = 5; // Forward Level or PWM signal, Active High
int lpwmPin = 6; // Reverse Level or PWM signal, Active High

// Enable-Pins
int rEnPin = 7; // Forward Drive Enable Input, Active High/Low Disable
int lEnPin = 8; // Reverse Drive Enable Input, Active High/Low Disable

void setup() {
  // PWM-Pins
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);

  // Enable-Pins
  pinMode(rEnPin, OUTPUT);
  pinMode(lEnPin, OUTPUT);

  // Anfangszustand: alles aus
  digitalWrite(rEnPin, LOW);
  digitalWrite(lEnPin, LOW);

  analogWrite(rpwmPin, 0);
  analogWrite(lpwmPin, 0);
}

void loop() {

  // ------------------------------
  // Motor vorwärts
  // ------------------------------
  digitalWrite(rEnPin, HIGH);   // Vorwärts aktivieren
  digitalWrite(lEnPin, LOW);    // Rückwärts deaktivieren

  for (int v = 0; v <= 255; v += 5) {
    analogWrite(rpwmPin, v);
    analogWrite(lpwmPin, 0);
    delay(30);
  }

  delay(800);

  // Stop
  analogWrite(rpwmPin, 0);
  digitalWrite(rEnPin, LOW);    // Aus
  delay(500);


  // ------------------------------
  // Motor rückwärts
  // ------------------------------
  digitalWrite(rEnPin, LOW);    // Vorwärts deaktivieren
  digitalWrite(lEnPin, HIGH);   // Rückwärts aktivieren

  for (int v = 0; v <= 255; v += 5) {
    analogWrite(lpwmPin, v);
    analogWrite(rpwmPin, 0);
    delay(30);
  }

  delay(800);

  // Stop
  analogWrite(lpwmPin, 0);
  digitalWrite(lEnPin, LOW);
  delay(1000);
}

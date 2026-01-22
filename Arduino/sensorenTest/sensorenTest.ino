// Pins
int TRIG_L = 2;
int ECHO_L = 3;

int TRIG_R = 7;
int ECHO_R = 8;

int TRIG_H = 11;
int ECHO_H = 12;

long messen(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long dauer = pulseIn(echoPin, HIGH, 30000); // max. 30 ms
  if (dauer == 0) return -1; // kein Echo
  return dauer * 0.034 / 2;
}

String bewertung(long abstand) {
  if (abstand == -1) return "Kein Signal";
  if (abstand < 20)  return "STOP!";
  if (abstand < 50)  return "ACHTUNG";
  return "OK";
}

void setup() {
  pinMode(TRIG_L, OUTPUT);
  pinMode(ECHO_L, INPUT);

  pinMode(TRIG_R, OUTPUT);
  pinMode(ECHO_R, INPUT);

  pinMode(TRIG_H, OUTPUT);
  pinMode(ECHO_H, INPUT);

  Serial.begin(9600);
  Serial.println("=== Einparkassistent gestartet ===");
}

void loop() {
  long links  = messen(TRIG_L, ECHO_L);
  delay(50);
  long rechts = messen(TRIG_R, ECHO_R);
  delay(50);
  long hinten = messen(TRIG_H, ECHO_H);

  Serial.println("-----------------------------");

  Serial.print("Links:  ");
  Serial.print(links);
  Serial.print(" cm  -> ");
  Serial.println(bewertung(links));

  Serial.print("Rechts: ");
  Serial.print(rechts);
  Serial.print(" cm  -> ");
  Serial.println(bewertung(rechts));

  Serial.print("Hinten: ");
  Serial.print(hinten);
  Serial.print(" cm  -> ");
  Serial.println(bewertung(hinten));

  delay(700);
}
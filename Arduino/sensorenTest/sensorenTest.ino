// Pins
int TRIG_L = 7;
int ECHO_L = 6;

int TRIG_R = 3;
int ECHO_R = 4;

int TRIG_H = 4;
int ECHO_H = 5;

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
}

void loop() {
  long links  = messen(TRIG_L, ECHO_L);
  long rechts = messen(TRIG_R, ECHO_R);
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
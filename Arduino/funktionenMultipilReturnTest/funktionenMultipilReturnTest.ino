int s, p;

void berechne(int a, int b, int *summe, int *produkt) {
  *summe = a + b;
  *produkt = a * b;
}

void setup() {
  Serial.begin(9600);

  berechne(4, 3, &s, &p);

}

void loop() {
  Serial.println(s);
  Serial.println(p);
}
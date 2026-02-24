const int potPin = A0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  int potValue = analogRead(potPin);
  Serial.println(potValue);

  delay(1000);
}
//365+ links
//365- rechts
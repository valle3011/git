const int lenkPin = A0;

const int rpwmPin = 8;
const int lpwmPin = 7;

int richtung = 0; //-1 ist ganz links, 0 ist mitte, +1 ist rechts

void setup() {
  // put your setup code here, to run once:
  pinMode(rpwmPin, OUTPUT);
  pinMode(lpwmPin, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int lenkValue = analogRead(lenkPin);
  //Serial.println(lenkValue);
  if (lenkValue >= 500) {
    Serial.println(richtung);
    Serial.println(lenkValue);
    lenkLinks();
    
  } else if (lenkValue <= 330) {
    Serial.println(richtung);
    Serial.println(lenkValue);
    lenkRechts();
  }
}

void lenkRechts() {
  if (richtung != 1) {
    static unsigned long startTime = 0;
    static bool aktiv = false;

    if (!aktiv) {
      analogWrite(rpwmPin, 255);
      analogWrite(lpwmPin, 0);
      Serial.println("Begin Rechts");
      startTime = millis();
      aktiv = true;
    }

    if (aktiv && millis() - startTime >= 800) { //800 als Variable für dynamisches Lenken
      analogWrite(rpwmPin, 0);
      Serial.println("Ende Rechts");
      Serial.println(millis());
      aktiv = false;
      richtung++;
    }
  }
}

void lenkLinks() {
  if (richtung != -1) {
    static unsigned long startTime = 0;
    static bool aktiv = false;

    if (!aktiv) {
      analogWrite(lpwmPin, 255);
      analogWrite(rpwmPin, 0);
      Serial.println("Begin Links");
      startTime = millis();
      aktiv = true;
    }

    if (aktiv && millis() - startTime >= 800) { //800 als Variable für dynamisches Lenken
      analogWrite(lpwmPin, 0);
      Serial.println("Ende Links");
      Serial.println(millis());
      aktiv = false;
      richtung--;
    }
  }
}
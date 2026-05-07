

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  delay(1500);                 // important: wait for USB serial
  Serial.println("READY");     // tell Pi we are alive
}

void loop() {

  // Read incoming serial text
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {           // full command received
      cmd.trim();
      processCommand(cmd);
      cmd = "";
    } else {
      cmd += c;
    }
  }
}

void processCommand(String s) {

  if (s == "LED ON") {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("OK");
    return;
  }

  if (s == "LED OFF") {
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("OK");
    return;
  }

  if (s == "PING") {
    Serial.println("PONG");
    return;
  }

  Serial.println("UNKNOWN");
}
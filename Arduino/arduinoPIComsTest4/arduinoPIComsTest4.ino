String cmd = "";

void setup() {
  // put your setup code here, to run once:
  Serial2.println("READY");

}

void loop() {
  // put your main code here, to run repeatedly:
  cmd = Serial2.read();
  cmd.trim();
  Serial2.println(cmd);
}

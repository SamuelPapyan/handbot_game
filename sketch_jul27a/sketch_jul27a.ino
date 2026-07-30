#define LED 13

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
}

void loop() {
  Serial.println("Hello World");
  delay(1000);
  // digitalWrite(LED, HIGH);
  // delay(100);
  // digitalWrite(LED, LOW);
  // delay(100);
}

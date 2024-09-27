#include <Arduino.h>


void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    int receivedByte = Serial.read();
    Serial.println(receivedByte);
  }
}
#include <Arduino.h>

int d = 250;
float start_bytes;
float value;
float end_bytes;
char buffer[40];

void setup() {
  // initialize the serial communication:
  Serial.begin(9600);
  
}

void loop() {
 // reply only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    start_bytes = Serial.parseFloat();
    value = Serial.parseFloat();
    end_bytes = Serial.parseFloat();

    // say what you got:
    sprintf(buffer, "start: %f angle: %f end: %f", start_bytes, value, end_bytes);
    Serial.println(buffer);
    
  }
}
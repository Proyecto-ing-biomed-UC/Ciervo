#include <Arduino.h>

int d = 250;
float X;
float Y;
char buffer[40];
void setup() {
  // initialize the serial communication:
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  
}

void loop() {
  digitalWrite(2, HIGH);
  delay(d);
  digitalWrite(2, LOW);
  delay(d);
 // reply only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    d = 1000;
    X = Serial.parseFloat();
    Y = Serial.parseFloat();

    // say what you got:
    sprintf(buffer, "X: %f Y: %f", X, Y);
    Serial.println(buffer);
    
  }
  else{
   Serial.println(buffer);  
d = 20;
  }
}
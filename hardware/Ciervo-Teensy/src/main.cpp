/// Librerias
#include <Arduino.h>
#include <Wire.h>

#define I2C_ADDRESS 0x08 // Dirección I2C de la Teensy 4.1

void receiveEvent(int);

int receivedNumber = 0;

void setup() {
  // Inicia la comunicación I2C
  Wire.begin(I2C_ADDRESS);
  
  // Configura el manejador para la recepción de datos I2C
  Wire.onReceive(receiveEvent);

  // Inicia la comunicación serial
  Serial.begin(9600);

  // Espera a que el puerto serial esté listo
  while (!Serial) {
    delay(10);
  }

  Serial.print("START");
}

void loop() {
  // Si se ha recibido un número, envíalo por el puerto serial
  if (receivedNumber != 0) {
    Serial.print("Número recibido: ");
    Serial.println(receivedNumber);
    
    // Resetea el número recibido para la próxima recepción
    receivedNumber = 0;
  }
  delay(100);
}

void receiveEvent(int howMany) {
  // Asegúrate de que el número de bytes recibidos sea correcto
  Wire.readBytes((char*)&receivedNumber, sizeof(int));
  //if (howMany == sizeof(int)) {
  //  // Lee los bytes recibidos y los convierte a un entero
  //  Wire.readBytes((char*)&receivedNumber, sizeof(int));
  //}
}

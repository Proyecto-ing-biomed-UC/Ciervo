#include <Arduino.h>
// Definir bytes de inicio y término
const byte START_BYTE = 0x02;  // Byte de inicio (STX)
const byte END_BYTE = 0x03;    // Byte de término (ETX)

// Buffer para almacenar los bytes recibidos
byte buffer[4];  // 4 bytes para almacenar el float
int bufferIndex = 0;
bool receiving = false;  // Estado para saber si estamos recibiendo un mensaje

// Variable donde se almacenará el valor float
float value = 0.0;

void setup() {
  Serial.begin(9600);  // Iniciar comunicación serial a 9600 baudios
  Serial.println("Esperando mensaje...");
}

void loop() {
  if (Serial.available() > 0) {
    byte incomingByte = Serial.read();

    // Si recibimos el byte de inicio, comenzamos a almacenar los bytes del float
    if (incomingByte == START_BYTE) {
      bufferIndex = 0;
      receiving = true;
    }
    // Si estamos recibiendo y aún no hemos almacenado 4 bytes
    else if (receiving) {
      if (bufferIndex < 4) {
        buffer[bufferIndex++] = incomingByte;
      }
      
      // Si ya hemos recibido los 4 bytes del float y el siguiente byte es el de término
      if (bufferIndex == 4 && incomingByte == END_BYTE) {
        // Convertir los bytes almacenados en un valor float
        memcpy(&value, buffer, sizeof(value));

        // Mostrar el valor recibido
        Serial.print("Float recibido: ");
        Serial.println(value);

        // Reiniciar el estado
        receiving = false;
      }
    }
  }
}

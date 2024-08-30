#include <Arduino.h>
#include <PID_v1.h>

#define PID_INPUT 41
#define PID_OUTPUT 3

#define LPWM_PIN 15
#define RPWM_PIN 14

#define ACE_ADDR 0x20
#include <ACE128.h>
#include <ACE128map87654321.h>

#ifdef ACE128_MCP23008
  #define ACE_PROBE_ADDR ACE_ADDR | 0x20
#else
  #define ACE_PROBE_ADDR ACE_ADDR
#endif

ACE128 myACE(ACE_ADDR, (uint8_t*)encoderMap_87654321); // I2C without using EEPROM

const int ZERO = 13;
uint8_t pinPos = 0; // pin values
uint8_t rawPos = 0;
uint8_t upos = 0;
uint8_t oldPos = 255;
int8_t pos;
int16_t mpos;
uint8_t seen = 0;

//Define Variables we'll be connecting to
double Setpoint, Input, Output;

//Specify the links and initial tuning parameters
double Kp=3, Ki=0, Kd=0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

float angle_setpoint;

void send_pid_value_to_motor(double);

void move_motor(uint8_t, uint8_t);

void setup_motor(void);

void setup_pid(void);

void setup_encoder(void);

void setup() {
  Serial.begin(9600);
  setup_motor();
  setup_pid();
  setup_encoder();
}

void loop() {
  if (Serial.available() >= 7) {  // Asegúrate de que hay al menos 7 bytes disponibles (2 bytes de header, 4 bytes de float, 1 byte de footer)
    // Leer los 2 bytes de header
    byte header1 = Serial.read();
    byte header2 = Serial.read();
    
    // Verificar el header
    if (header1 == 0xAA && header2 == 0xBB) {
      // Leer el float
      byte floatBytes[4];
      for (int i = 0; i < 4; i++) {
        floatBytes[i] = Serial.read();
      }
      
      // Convertir los 4 bytes a un float
      float valorRecibido;
      memcpy(&valorRecibido, floatBytes, sizeof(valorRecibido));
      
      // Leer el byte de footer
      byte footer = Serial.read();
      
      // Verificar el footer
      if (footer == 0xCC) {
        // Si el mensaje es válido, imprimir el valor float
        //Serial.print("Valor recibido: ");
        //Serial.println(valorRecibido);

        Setpoint = valorRecibido;
      } else {
        Serial.println("Footer incorrecto");
      }
    } else {
      Serial.println("Header incorrecto");
    }
  }

  if (digitalRead(ZERO) == 0) {     // check set-zero button
          myACE.setMpos(0);               // set logical multiturn zero to current position
          oldPos = 255;                   // force display update
        }

        pinPos = myACE.acePins();          // get IO expander pins - this is for debug
        rawPos = myACE.rawPos();           // get raw mechanical position - this for debug
        pos = myACE.pos();                 // get logical position - signed -64 to +63
        upos = myACE.upos();               // get logical position - unsigned 0 to +127
        mpos = myACE.mpos();               // get multiturn position - signed -32768 to +32767

        Input = map(rawPos, 0, 127, 0, 360);

        myPID.Compute();
        send_pid_value_to_motor(Output);

        // Carácter de inicio y término
        char startChar = '<';
        char endChar = '>';

        // Enviar el carácter de inicio
        Serial.write(startChar);

        // Enviar los números como bytes
        Serial.write((byte*)&Setpoint, sizeof(double));
        Serial.write((byte*)&Input, sizeof(double));
        Serial.write((byte*)&Output, sizeof(double));

        // Enviar el carácter de término
        Serial.write(endChar);
}

void send_pid_value_to_motor(double pid_value){

  if (pid_value >= 0){
    move_motor(abs(pid_value), 1);
  }

  else {
    move_motor(abs(pid_value), 0);
  }
}

void move_motor(uint8_t value, uint8_t direction){
    if (direction == 1){
        analogWrite(RPWM_PIN, value); //hacia delante
        analogWrite(LPWM_PIN, 0);
    }

    else if (direction == 0){
        analogWrite(RPWM_PIN, 0); //hacia atras
        analogWrite(LPWM_PIN, value);
    }
}

void setup_motor(void){
    pinMode(RPWM_PIN, OUTPUT);
    pinMode(LPWM_PIN, OUTPUT);
}

void setup_pid(void){
  //initialize the variables we're linked to
  //Input = 110;
  //Setpoint = 100;

  //turn the PID on
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-255, 255);
}

void setup_encoder(void){
  Wire.begin();
  int error = 1;

  while (error != 0){
    Wire.beginTransmission(ACE_PROBE_ADDR);
    error = Wire.endTransmission();
    delay(100);
  }

  myACE.begin();

  pinPos = myACE.acePins();          // get IO expander pins
  oldPos = pinPos;                 // remember where we are

  pinMode(ZERO, INPUT_PULLUP);    // configure set-zero button
}


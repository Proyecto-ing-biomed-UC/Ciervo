#include <Arduino.h>
#include <PID_v1.h>

#define ACE_ADDR 0x20
#include <ACE128.h>
#include <ACE128map87654321.h>
//#include <Adafruit_MAX31865.h>

#ifdef ACE128_MCP23008
  #define ACE_PROBE_ADDR ACE_ADDR | 0x20
#else
  #define ACE_PROBE_ADDR ACE_ADDR
#endif

#define PID_INPUT 41
#define PID_OUTPUT 3

#define LPWM_PIN 22
#define RPWM_PIN 15

#define MIN_ANGLE 95
#define MAX_ANGLE 175

#define MIN_ANGLE_LIMIT_SWITCH 28     // Not definitive yet
#define MAX_ANGLE_LIMIT_SWITCH 29     //



//    Serial Configuration
#define SERIAL_BAUD 9600

#define TIMEOUT 3000

//#define USE_UART                    //Uncomment to use

#define ECHO_MODE                   //Uncomment to use

#ifdef USE_UART
    #define SERIAL_PORT Serial8
#else
    #define SERIAL_PORT Serial
#endif

unsigned long lastReceiveTime = 0; 

ACE128 myACE(ACE_ADDR, (uint8_t*)encoderMap_87654321); // I2C without using EEPROM
//Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 11, 12, 13); // Temperature sensor

// Variable donde se almacenará el valor float
float value = 0.0;

const int ZERO = 16;  // Original = 13, cambiado por coflicto con pines SPI

uint8_t pinPos = 0; // pin values
uint8_t rawPos = 0;
uint8_t oldPos = 255;
int16_t mpos;

//Define Variables we'll be connecting to
double Setpoint, Input, Output;

//Specify the links and initial tuning parameters
double Kp=6, Ki=0, Kd=0;
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

float angle_setpoint;

void send_pid_value_to_motor(double);

void move_motor(uint8_t, uint8_t);

void setup_motor(void);

void setup_pid(void);

void setup_encoder(void);

void setup() {
  SERIAL_PORT.begin(SERIAL_BAUD);
  setup_motor();
  setup_pid();
  setup_encoder();

  //  Assuming the limit switch is in pullup configuration
  pinMode(MIN_ANGLE_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(MAX_ANGLE_LIMIT_SWITCH, INPUT_PULLUP);
}

void loop() {
  if (Serial.available() > 0) {
    int receivedByte = Serial.read();

    // Limit angle setpoint range
    // Comment to remove limit
    if (receivedByte > MAX_ANGLE){
      receivedByte = MAX_ANGLE;
    }
    else if (receivedByte < MIN_ANGLE){
      receivedByte = MIN_ANGLE;
    }

    Setpoint = (double)receivedByte;

    lastReceiveTime = millis();
  
  }

  #ifdef ECHO_MODE
    SERIAL_PORT.println((int)Input);
  #endif

  

  if (millis() - lastReceiveTime > TIMEOUT) {
    Setpoint = (double)MAX_ANGLE;
  }

  if (digitalRead(ZERO) == 0) {     // check set-zero button
          myACE.setMpos(0);               // set logical multiturn zero to current position
          oldPos = 255;                   // force display update
  }

  pinPos = myACE.acePins();          // get IO expander pins - this is for debug
  rawPos = myACE.rawPos();           // get raw mechanical position - this for debug

  //int min_switch_val = digitalRead(MIN_ANGLE_LIMIT_SWITCH);
  //int max_switch_val = digitalRead(MAX_ANGLE_LIMIT_SWITCH);


  

  
    Input = 360 - (171 + map(rawPos, 0, 127, 0, 360));

    myPID.Compute();

    send_pid_value_to_motor(Output);
  
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

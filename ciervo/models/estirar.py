import os; os.system('clear')
from paho.mqtt import client as mqtt_client
from ciervo.models import features_v1
import numpy as np
import ciervo.parameters as p
from ciervo.aux_tools import Buffer
import time
import joblib
import serial
import struct


broker = p.BROKER_HOST
port = 1883
topic = "data"


class SendAngleSerial:

    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0',
                                 baudrate=9600,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=1)
        time.sleep(1)

    def send_float_via_serial(self, value):
        # Send int
        int_value = int(value)
        if 0 <= int_value <= 255:
            self.ser.write(bytes([int_value]))
        else:
            if int_value > 255:
                self.ser.write(bytes([255]))
            
            elif int_value < 0:
                self.ser.write(bytes([0]))



if __name__ == '__main__':

    send = SendAngleSerial()
    print("Enviado")
    send.send_float_via_serial(180)
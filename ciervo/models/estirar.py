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
from threading import Thread


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
        
        self.msg_tx = 0
        self.msg_rx = 0

        time.sleep(2)

        frequency = 10 # Hz

        #thread = Thread(target = self.read_byte_loop, args=())
        #thread.deamon = True
        #thread.start()

    def send_byte(self, value):
        # Send int
        int_value = int(value)

        if 0 <= int_value <= 255:
            pass
        else:
            if int_value > 255:
                int_value = 255
            
            elif int_value < 0:
                int_value = 0

        self.ser.write(bytes([int_value]))

        self.msg_tx = int_value

        print(f'raw_msg:\t{value}\t,\tmsg_tx:\t{self.msg_tx}\t,\tmsg_rx:\t{self.msg_rx}')
    
    def read_byte(self):
        if self.ser.in_waiting > 0:
            received_data = self.ser.readline()
            #received_value = int.from_bytes(received_data, byteorder='big')
            decoded_data = received_data.decode('utf-8').strip()
            int_val = int(decoded_data)

            self.msg_rx = int_val

            return received_data
    
    def read_byte_loop(self):
        try:
            while True:
                self.read_byte()

        except:
            return


if __name__ == '__main__':

    send = SendAngleSerial()
    print("Enviado")




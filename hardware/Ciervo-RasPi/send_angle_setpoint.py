import struct
import serial
import time

import random

from threading import Thread

ser = serial.Serial('COM13', 9600, timeout=1)

#print(ser)
time.sleep(3)

def sendmess():
    value = 90.0
    print(f"Send: {value}")
    #bin_msg = str(value) + '\n' #Pack float value into 4 bytes
    bin_msg = struct.pack('f',value)
    data = ser.write(bin_msg)
    echo = ser.readline()
    print("Echo: " + str(echo))
    #ser.close()

while True:
    sendmess()
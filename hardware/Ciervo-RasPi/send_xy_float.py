import struct
import serial
import time
x=0.8
y=0.2

ser = serial.Serial('COM5', 9600, timeout=1)

#print(ser)
time.sleep(3)

def sendmess():
    bin = str(x) + str(y) #Pack float value into 4 bytes
    data = ser.write(bin.encode())
    echo = ser.readline()
    print("Echo: " + echo)
    #ser.close()

while True:
    sendmess()
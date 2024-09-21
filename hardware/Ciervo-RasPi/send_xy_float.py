import struct
import serial
import time
start   = 0.1
value   = 90.0
end     = 0.9

ser = serial.Serial('COM13', 9600, timeout=1)

#print(ser)
time.sleep(3)

def sendmess():
    bin = str(start) + str(value) + str(end) #Pack float value into 4 bytes
    data = ser.write(bin.encode())
    echo = ser.readline()
    print("Echo: " + echo)
    #ser.close()

while True:
    sendmess()
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
    #bin_msg = str(value) + '\n'
    bin_msg = struct.pack('f',value)
    data = ser.write(bin_msg.encode())
    echo = ser.readline()
    print("Echo: " + echo)
    #ser.close()

while True:
    sendmess()
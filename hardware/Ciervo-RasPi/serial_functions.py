import serial
import time
from threading import Thread

def send_byte(value, ser, echo=False):
    int_value = int(value)
    if 0 <= int_value <= 255:
        ser.write(bytes([int_value]))
    else:
        if int_value > 255:
            ser.write(bytes([255]))
        
        elif int_value < 0:
            ser.write(bytes([0]))
    
    if echo:
        print(f'Send value: {value}')

def read_byte(ser, echo=False):
    if ser.in_waiting > 0:
        received_data = ser.read(1)
        received_value = int.from_bytes(received_data, byteorder='big')
        if echo:
            print(f"Received value: {received_value}")
        return received_value

def read_byte_loop(ser):
    try:
        while True:
            read_byte(ser, echo=True)
    
    except:
        return



if __name__ == '__main__':
    try:
        serial_port = serial.Serial('COM13', 9600)
        time.sleep(2)

        thread = Thread(target = read_byte_loop, args=(serial_port,))
        thread.start()

        angle = 92.5

        while True:
            send_byte(angle, serial_port, echo=True)
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Terminando...")
        serial_port.close()







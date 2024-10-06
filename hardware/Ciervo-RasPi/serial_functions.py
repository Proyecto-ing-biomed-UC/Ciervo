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
        received_data = ser.readline()
        #received_value = int.from_bytes(received_data, byteorder='big')
        decoded_data = received_data.decode('utf-8').strip()
        int_val = int(decoded_data)
        if echo:
            print(f"Received value: {int_val}")
        return received_data

def read_byte_loop(ser):
    try:
        while True:
            read_byte(ser, echo=True)
    
    except:
        return



if __name__ == '__main__':
    try:
        serial_port = serial.Serial(port='COM13',
                         baudrate=9600,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=1)
        time.sleep(2)

        frequency = 10 # Hz

        thread = Thread(target = read_byte_loop, args=(serial_port,))
        thread.start()

        angle = 0.3

        while True:
            send_byte(angle, serial_port, echo=True)
            angle += 1.0

            if angle > 255.0:
                angle = 0.3
                
            time.sleep(1.0/frequency)
    
    except KeyboardInterrupt:
        print("Terminando...")
        serial_port.close()







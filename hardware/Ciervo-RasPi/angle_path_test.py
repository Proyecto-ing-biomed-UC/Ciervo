import struct
import serial
import numpy as np
from threading import Thread
from time import sleep

def send_message(serial_port, message, header=b'\xAA\xBB', footer=b'\xCC'):
    # Empaquetar el float en formato de 4 bytes (32 bits)
    mensaje_empaquetado = struct.pack('>f', message)
    
    # Crear el mensaje completo concatenando header + mensaje + footer
    mensaje_completo = header + mensaje_empaquetado + footer
    
    # Enviar el mensaje por el puerto serial
    serial_port.write(mensaje_completo)

def read_double(serial_port):
    """Lee un número double del puerto serial"""
    return struct.unpack('d', serial_port.read(8))[0]

def read_message(serial_port):
    """Lee el mensaje completo desde el puerto serial"""
    # Buscar el carácter de inicio '<'
    while serial_port.read(1) != b'<':
        pass

    # Leer los tres números double
    num1 = read_double(serial_port)
    num2 = read_double(serial_port)
    num3 = read_double(serial_port)

    # Buscar el carácter de término '>'
    while serial_port.read(1) != b'>':
        pass

    return num1, num2, num3

def loop_read(ser):
    while True:
        double_setpoint, double_input, double_output = read_message(ser)
        print(f'setpoint: {double_setpoint}\ninput: {double_input}\noutput: {double_output}')

angle_data = np.genfromtxt('./data/angle.csv', delimiter=',')

ser = serial.Serial('COM5', baudrate=9600, timeout=1) # Cambiar segun el puerto al que esta conectada la teensy

frequency = 1.0 # Hz, cambiar a conveniencia

thread = Thread(target = loop_read, args = (ser, ))
thread.start()

for angle in angle_data:
    print(f'>>>{angle}')
    send_message(ser, angle)
    sleep(1/frequency)


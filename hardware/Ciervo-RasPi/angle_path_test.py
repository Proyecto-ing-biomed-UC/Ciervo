import struct
import serial
import numpy as np
import time

def send_message(serial_port, message, header=b'\xAA\xBB', footer=b'\xCC'):
    # Empaquetar el float en formato de 4 bytes (32 bits)
    mensaje_empaquetado = struct.pack('>f', message)
    
    # Crear el mensaje completo concatenando header + mensaje + footer
    mensaje_completo = header + mensaje_empaquetado + footer
    
    # Enviar el mensaje por el puerto serial
    serial_port.write(mensaje_completo)


angle_data = np.genfromtxt('./data/angle.csv', delimiter=',')

ser = serial.Serial('COM0', baudrate=9600, timeout=1) # Cambiar segun el puerto al que esta conectada la teensy

frequency = 1.0 # Hz, cambiar a conveniencia

for angle in angle_data:
    send_message(ser, angle)
    time.sleep(1/frequency)


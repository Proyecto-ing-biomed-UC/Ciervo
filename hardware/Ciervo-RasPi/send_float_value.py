import serial
import struct
import time
import random
from threading import Thread
import numpy as np

# Configurar el puerto serial (ajusta el puerto y baudrate según sea necesario)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Reemplaza 'COM3' por tu puerto serial
time.sleep(2)  # Espera a que se inicialice la conexión serial

# Definir bytes especiales para inicio y término del mensaje
START_BYTE = b'\x02'  # Byte de inicio (0x02 = STX en ASCII)
END_BYTE = b'\x03'    # Byte de término (0x03 = ETX en ASCII)

def send_float_via_serial(value):
    # Convertir el número float a 4 bytes usando formato 'f' de struct
    float_bytes = struct.pack('f', value)
    
    # Construir el mensaje: [START_BYTE] + [FLOAT_BYTES] + [END_BYTE]
    message = START_BYTE + float_bytes + END_BYTE
    
    # Enviar el mensaje a través del puerto serial
    ser.write(message)
    print(f"Enviado: {value}")# como mensaje: {message}")

def receive_message_from_arduino():
    # leer datos del Arduino si hay disponibles
    if ser.in_waiting > 0:
        # Leer la respuesta completa hasta encontrar un salto de línea
        response = ser.read_until().decode('utf-8').strip()
        print(f"Mensaje recibido: {response}")

def receive_message_thread():
    while True:
        receive_message_from_arduino()

    
# Ejemplo de uso
try:
    thread = Thread(target = receive_message_thread)
    thread.start()
    number = 0.0
    numbers = [90.0, 100.0,120.0, 150.0, 160.0, 100.0, 170.0]
    i = 0

    angle_data = np.genfromtxt('/home/eoweo/Ciervo/hardware/Ciervo-RasPi/data/angle.csv', delimiter=',')

    for angle in angle_data:
        number = numbers[i]

        # Enviar el float con bytes de inicio y término

        if not np.isnan(angle):
            #print(angle)
            send_float_via_serial(number)
        
        time.sleep(5)
        
        # Esperar antes d
        i += 1
        if i == len(numbers):
            i = 0

except KeyboardInterrupt:
    print("Terminando...")
    ser.close()


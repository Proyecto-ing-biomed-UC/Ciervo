import serial
import struct
import time
import random

# Configurar el puerto serial (ajusta el puerto y baudrate según sea necesario)
ser = serial.Serial('COM13', 9600, timeout=1)  # Reemplaza 'COM3' por tu puerto serial
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
    # Leer datos del Arduino si hay disponibles
    if ser.in_waiting > 0:
        # Leer la respuesta completa hasta encontrar un salto de línea
        response = ser.readline().decode('utf-8').strip()
        print(f"Mensaje recibido: {response}")

# Ejemplo de uso
try:
    number = 0.0
    numbers = [0.0, 64.0, 127.0, 127.0 + 64.0, 255.0]
    i = 0
    while True:
        # Pide un valor flotante
        #number += 0.1#float(input("Ingresa un número float para enviar: "))
        number = numbers[i]
        
        # Enviar el float con bytes de inicio y término
        send_float_via_serial(number)
        
        # Leer y mostrar los mensajes recibidos del Arduino
        #receive_message_from_arduino()
        
        # Esperar antes de enviar otro dato
        time.sleep(0.1)
        i += 1
        if i == len(numbers):
            i = 0

except KeyboardInterrupt:
    print("Terminando...")
    ser.close()


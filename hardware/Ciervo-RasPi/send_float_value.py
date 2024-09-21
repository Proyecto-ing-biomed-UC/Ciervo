import serial
import struct
import time

# Configurar el puerto serial (ajusta el puerto y baudrate según sea necesario)
ser = serial.Serial('COM13', 9600)  # Reemplaza 'COM3' por tu puerto serial
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
    print(f"Enviado: {value} como mensaje: {message}")

# Ejemplo de uso
try:
    while True:
        # Pide un valor flotante
        number = float(input("Ingresa un número float para enviar: "))
        
        # Enviar el float con bytes de inicio y término
        send_float_via_serial(number)
        
        # Esperar antes de enviar otro dato
        time.sleep(1)

except KeyboardInterrupt:
    print("Terminando...")
    ser.close()

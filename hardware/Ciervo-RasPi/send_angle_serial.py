import struct
import serial

# Configuración del puerto serial (ajusta según tu puerto)
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

def enviar_mensaje(header, mensaje_float, footer):
    # Empaquetar el float en formato de 4 bytes (32 bits)
    mensaje_empaquetado = struct.pack('>f', mensaje_float)
    
    # Crear el mensaje completo concatenando header + mensaje + footer
    mensaje_completo = header + mensaje_empaquetado + footer
    
    # Enviar el mensaje por el puerto serial
    ser.write(mensaje_completo)

# Definir header, footer y mensaje float
header = b'\xAA\xBB'  # Ejemplo de 16 bits de header
mensaje_float = 3.14159  # Ejemplo de mensaje float
footer = b'\xCC'  # Ejemplo de 8 bits de término de mensaje

# Enviar el mensaje
enviar_mensaje(header, mensaje_float, footer)

# Cerrar el puerto serial
ser.close()
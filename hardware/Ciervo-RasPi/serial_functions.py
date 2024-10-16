import serial
import time
from threading import Thread

msg_sent = 0
msg_received = 0 

def send_byte(value, ser, echo=False):

    global msg_sent

    int_value = int(value)

    if 0 <= int_value <= 255:
        pass
    else:
        if int_value > 255:
            int_value = 255
        
        elif int_value < 0:
            int_value = 0
    
    ser.write(bytes([int_value]))

    msg_sent = int_value
    
    if echo:
        print(f'Send value: {value}')

def read_byte(ser, echo=False):

    global msg_received

    if ser.in_waiting > 0:
        received_data = ser.readline()
        #received_value = int.from_bytes(received_data, byteorder='big')
        decoded_data = received_data.decode('utf-8').strip()
        int_val = int(decoded_data)

        msg_received = int_val

        if echo:
            print(f"Received value: {int_val}")
        return received_data

def read_byte_loop(ser):
    try:
        while True:
            read_byte(ser)
    
    except:
        return



if __name__ == '__main__':
    try:
        port_names = {
            'WINDOWS'   :   'COM13',
            'LINUX'     :   '/dev/ttyACM0',
            'RASPI_USB' :   '/dev/ttyACM0',
            'RASPI_UART':   '/dev/ttyS0'
            }
        
        port = 'LINUX'
        baudrate = 9600

        serial_port = serial.Serial(port=port_names[port],
                         baudrate=baudrate,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=1)
        time.sleep(2)

        frequency = 10 # Hz

        thread = Thread(target = read_byte_loop, args=(serial_port,))
        thread.start()

        angle = 95.0

        while True:
            send_byte(angle, serial_port)
            angle += 0.5

            if angle > 175.0:
                angle = 95.0
            
            print(f'raw_msg:\t{angle}\t,\tmsg_tx:\t{msg_sent}\t,\tmsg_rx:\t{msg_received}')
                
            time.sleep(1.0/frequency)
    
    except KeyboardInterrupt:
        print("Terminando...")
        serial_port.close()







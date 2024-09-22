import os; os.system('clear')
from paho.mqtt import client as mqtt_client
from ciervo.models import features_v1
import numpy as np
import ciervo.parameters as p
from ciervo.aux_tools import Buffer
import time
import joblib
import serial
import struct


broker = p.BROKER_HOST
port = 1883
topic = "data"


# Definir bytes especiales para inicio y término del mensaje
START_BYTE = b'\x02'  # Byte de inicio (0x02 = STX en ASCII)
END_BYTE = b'\x03'    # Byte de término (0x03 = ETX en ASCII)

class SendAngleSerial:

    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Reemplaza 'COM3' por tu puerto serial
        time.sleep(2)

    def send_float_via_serial(self, value):
        # Convertir el número float a 4 bytes usando formato 'f' de struct
        float_bytes = struct.pack('f', value)
        
        # Construir el mensaje: [START_BYTE] + [FLOAT_BYTES] + [END_BYTE]
        message = START_BYTE + float_bytes + END_BYTE
        
        # Enviar el mensaje a través del puerto serial
        self.ser.write(message)
        print(f"Enviado: {value}")# como mensaje: {message}")



class RealTimeInference:
    def __init__(self, 
                 window=0.1, 
                 emg_prepro=None, 
                 emg_model=None, 
                 emg_idx=[0, 1, 2, 3],
                 acc_idx=[8, 9, 10],
                 serial_send=False,
                 ):
        self.update_speed = 1/10 # seconds
        self.window = window  # seconds
        self.angle_speed = 5 # degrees per second
        self.serial_send = serial_send

        self.emg_idx = emg_idx
        self.acc_idx = acc_idx

        if self.serial_send:
            self.serial = SendAngleSerial()

        # Angle
        self._angle = 0

        # preprocesamiento
        self.emg_prepro = emg_prepro

        # modelo
        self.emg_model = emg_model
        if self.emg_model is not None:
            self.emg_model = joblib.load(emg_model)

        # Buffer
        self.buffer = Buffer(self.window, roll=True)

        # pre-compile emg_prepro
        if self.emg_prepro is not None:
            self.emg_prepro(self.buffer.data[self.emg_idx, :])


        # MQTT
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, 'inference')
        self.client.on_connect = on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.subscribe(topic)
        self.client.loop_start()

        self.update()

    @property
    def angle(self):
        return self._angle
    
    @angle.setter
    def angle(self, value):
        # min 0, max 180
        self._angle = value % 180

    def on_message(self, client, userdata, msg):
        # Actualizar buffer
        data = np.frombuffer(msg.payload, dtype=p.PRECISION)
        data = data.reshape(p.NUM_CHANNELS, -1)
        self.buffer.data = data

    def update(self):
        while True:
            tic = time.time()
            data = self.buffer.data
            
            # data
            emg = data[self.emg_idx, :]
            #acc = data[self.acc_idx, :]
            if self.emg_prepro is not None:
                features, _ = self.emg_prepro(emg) # (C, T)
                # add dimension
                features = features.reshape(1, -1)
            
            if self.emg_model is not None:
    
                prediction = self.emg_model.predict(features)[0]
                
                # Update angle
                if prediction == 1:
                    self.angle +=  np.random.randint(-10, 10)
                else:
                    self.angle -=  np.random.randint(-10, 10)

                # Send angle
                if self.serial_send:
                    self.serial.send_float_via_serial(self.angle)

                self.client.publish('marker', self.angle, qos=0)



            toc = time.time()
            #print((toc-tic)/self.update_speed)
            time.sleep(np.max([self.update_speed - (toc-tic), 0]))


 


# The callback function of connection
def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe('data')


if __name__ == '__main__':

    RealTimeInference(
        emg_prepro=features_v1, 
        emg_model='model.pkl',
        serial_send=False,
        )
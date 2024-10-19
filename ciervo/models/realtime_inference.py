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
from threading import Thread


broker = p.BROKER_HOST
port = 1883
topic = "data"


class SendAngleSerial:

    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0',
                                 baudrate=9600,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=1)
        
        self.msg_tx = 0
        self.msg_rx = 0

        time.sleep(2)

        frequency = 10 # Hz

        thread = Thread(target = self.read_byte_loop, args=())
        thread.start()

    def send_byte(self, value):
        # Send int
        int_value = int(value)

        if 0 <= int_value <= 255:
            pass
        else:
            if int_value > 255:
                int_value = 255
            
            elif int_value < 0:
                int_value = 0

        self.ser.write(bytes([int_value]))

        self.msg_tx = int_value

        print(f'raw_msg:\t{value}\t,\tmsg_tx:\t{self.msg_tx}\t,\tmsg_rx:\t{self.msg_rx}')
    
    def read_byte(self):
        if self.ser.in_waiting > 0:
            received_data = self.ser.readline()
            #received_value = int.from_bytes(received_data, byteorder='big')
            decoded_data = received_data.decode('utf-8').strip()
            int_val = int(decoded_data)

            self.msg_rx = int_val

            return received_data
    
    def read_byte_loop(self):
        try:
            while True:
                self.read_byte()

        except:
            return



class RealTimeInference:
    def __init__(self, 
                 window=0.1, 
                 emg_prepro=None, 
                 emg_model=None, 
                 emg_idx=[0, 1, 2, 3],
                 acc_idx=[8, 9, 10],
                 serial_send=True,
                 ):
        self.update_speed = 1/5 # seconds
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
        # min 90, max 180
        self._angle = np.clip(value, 90, 175)

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
                #print("prediccion", prediction)
                # Update angle
                if prediction == 1: #activa
                    self.angle +=  30
                else: 
                    self.angle =  90

                # Send angle
                if self.serial_send:
                    self.serial.send_byte(self.angle)

                self.client.publish('marker', int(self._angle), qos=0)
                #print(self.angle)



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
        serial_send=True,
        )

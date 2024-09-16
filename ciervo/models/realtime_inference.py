import os; os.system('clear')
from paho.mqtt import client as mqtt_client
from ciervo.models import features_v1
import numpy as np
import ciervo.parameters as p
from ciervo.aux_tools import Buffer
import time


broker = p.BROKER_HOST
port = 1883
topic = "data"



class RealTimeInference:
    def __init__(self, 
                 window=5, 
                 emg_prepro=None, 
                 emg_model=None, 
                 emg_idx=[0, 1, 2, 3, 4, 5, 6, 7],
                 acc_idx=[8, 9, 10]
                 ):
        self.update_speed = 1/60 # seconds
        self.window = window  # seconds
        self.num_points = self.window * 250

        self.emg_idx = emg_idx
        self.acc_idx = acc_idx

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
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, 'plotter')
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
        if value < 0:
            value = 0
        elif value > 180:
            value = 180


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
                features, _ = self.emg_prepro(emg)
            
            if self.emg_model is not None:
                prediction = self.emg_model.predict(features)
                print(prediction)
                
            


                #self.client.publish('angle/inference', self.angle, qos=0)


            toc = time.time()
            print((toc-tic)/self.update_speed)
            time.sleep(np.max([self.update_speed - (toc-tic), 0]))


 


# The callback function of connection
def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe('data')


if __name__ == '__main__':

    RealTimeInference(emg_prepro=features_v1, emg_model='model.pkl')
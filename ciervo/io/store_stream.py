import os; os.system('clear')
from paho.mqtt import client as mqtt_client
import numpy as np
import ciervo.parameters as p
from ciervo.aux_tools import Buffer
import re
from time import sleep

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


broker = p.BROKER_HOST
port = 1883
topic = "data"


class StoreStream:
    def __init__(self, folder='recordings', duration=60*60*3):
        self.duration = duration  # in seconds
        self.num_points = self.duration * p.SAMPLE_RATE
        self.folder = folder

        # Buffer
        self.file_num = 0
        self.buffer = Buffer(self.duration)

        # MQTT
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, 'saver')
        self.client.on_connect = on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.subscribe(topic)
        self.client.loop_start()

        sleep(1)

        # File name input
        print("Enter file name: ", end='')
        self.file_name = input()
        if '.npy' not in self.file_name:
            self.file_name += '.npy'


        while True:
            # Ask to stop the recording
            print("Press 'q' to stop recording: ", end='')
            command = input()
            if command == 'q':
                self.client.loop_stop()
                break
        
        self.save_data()



    def on_message(self, client, userdata, msg):
        data = np.frombuffer(msg.payload, dtype=p.PRECISION)
        data = data.reshape(6, -1)
        self.buffer.data = data


    def save_data(self):
        filename = os.path.join(self.folder, f"{self.file_name}")
        np.save(filename, self.buffer.data[:, :self.buffer.idx])
        print(f"Data saved to {filename}")
        self.file_num += 1

# The callback function of connection
def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe('data')


def verify_recording(folder):
    files = os.listdir(folder)
    files = natural_sort([f for f in files if f.endswith('.npy')])
    data = []
    for f in files:
        data.append(np.load(os.path.join(folder, f)))
    data = np.concatenate(data, axis=1)

    channels, points = data.shape
    print(f"Data shape: {data.shape}")
    print(f"Number of channels: {channels}")
    print(f"Number of points: {points}")
    print(f"Duration: {points / p.SAMPLE_RATE} seconds")

    print(set(np.diff(data[0])))




if __name__ == '__main__':
    StoreStream()
    verify_recording('recordings')


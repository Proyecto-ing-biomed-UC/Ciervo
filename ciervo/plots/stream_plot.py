# python 3.11
import os; os.system('clear')
import random
from paho.mqtt import client as mqtt_client
import numpy as np
import time
import pyqtgraph as pg
from brainflow.data_filter import DataFilter, DetrendOperations
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import ciervo.parameters as p


broker = p.BROKER_HOST
port = 1883
topic = "data"
client_id = f'subscribe-{random.randint(0, 100)}'




class Graph:
    def __init__(self):
        self.update_speed_ms = 50
        self.window_size = 20
        self.num_points = self.window_size * 250

        # MQTT
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, 'plotter')
        self.client.on_connect = on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.subscribe(topic)
        self.client.loop_start()

        # Buffer
        self.buffer = Buffer(self.window_size)


        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow(title='BrainFlow Plot', size=(800, 600))

        self._init_timeseries()

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)
        QtGui.QApplication.instance().exec_()


    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i in range(8):
            p = self.win.addPlot(row=i, col=0)
            p.showAxis('left', False)
            p.setMenuEnabled('left', False)
            if i == 7:
                p.showAxis('bottom', True)
            else:
                p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            p.setLabel('left', f'EMG {i+1}')
            if i == 0:
                p.setTitle('TimeSeries Plot')
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)

    def on_message(self, client, userdata, msg):
        data = np.frombuffer(msg.payload, dtype=p.PRECISION)
        data = data.reshape(6, -1)
        self.buffer.data = data

    def update(self):
        data = self.buffer.data
        for count, channel in enumerate(range(6)):
            self.curves[count].setData(data[channel].tolist())

        self.prev_time = data
        self.app.processEvents()


# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe('data')


class Buffer:
    def __init__(self, duration):
        self.window = duration * p.SAMPLE_RATE
        self._data = np.zeros((p.NUM_CHANNELS, self.window ), dtype=p.PRECISION)
        self.idx = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = np.concatenate((self._data, data), axis=1)[:, -self.window:]







if __name__ == '__main__':
    Graph()
    bu  = Buffer(4)

    print(bu.data.shape)
    bu.data = np.random.randn(p.NUM_CHANNELS, 10)
    print(bu.data.shape)


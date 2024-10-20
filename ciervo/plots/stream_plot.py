import os; os.system('clear')
from paho.mqtt import client as mqtt_client
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import ciervo.parameters as p
from ciervo.aux_tools import Buffer
import argparse


broker = '192.168.0.101'
port = 1883
topic = "data"



class Graph:
    def __init__(self, window=5):
        self.update_speed_ms = 50
        self.window = window
        self.num_points = self.window * 250

        # MQTT
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, 'plotter')
        self.client.on_connect = on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.client.subscribe(topic)
        self.client.loop_start()

        # Buffer
        self.buffer = Buffer(self.window, roll=True)


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
        for i in range(p.NUM_CHANNELS):
            po = self.win.addPlot(row=i, col=0)
            po.showAxis('left', False)
            po.setMenuEnabled('left', False)

            if 'C' in p.CH_NAMES[i]:
                po.setYRange(-50, 50)

            if 'MARKERS' in p.CH_NAMES[i]:
                po.setYRange(90, 180)

            if 'AX' in p.CH_NAMES[i]:
                po.setYRange(-1, 1)

            if 'AY' in p.CH_NAMES[i]:
                po.setYRange(-1, 1)

            if 'AZ' in p.CH_NAMES[i]:
                po.setYRange(-1, 1)

            # Add time axis to the last plot
            if i == p.NUM_CHANNELS - 1:
                po.showAxis('bottom', True)
            else:
                po.showAxis('bottom', False)
            po.setMenuEnabled('bottom', False)

            # Y axis label
            po.setLabel('left', p.CH_NAMES[i])
     

            if i == 0:
                po.setTitle('TimeSeries Plot')
            self.plots.append(po)
            curve = po.plot()
            self.curves.append(curve)

    def on_message(self, client, userdata, msg):
        data = np.frombuffer(msg.payload, dtype=p.PRECISION)
        data = data.reshape(p.NUM_CHANNELS, -1)
        self.buffer.data = data

        #print(self.buffer.data.shape)

    def update(self):
        data = self.buffer.data
        if data.shape[1] == 0:
            return
        for count, channel in enumerate(range(p.NUM_CHANNELS)):
            self.curves[count].setData(data[channel].tolist())

        self.prev_time = data
        self.app.processEvents()


# The callback function of connection
def on_connect(client, userdata, flags, rc, properties):
    print(f"Connected with result code {rc}")
    client.subscribe('data')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--window', type=int, help='duration of the recording', required=False, default=5)
    
    args = parser.parse_args()

    Graph(window=args.window)
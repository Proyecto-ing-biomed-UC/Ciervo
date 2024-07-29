import numpy as np
import ciervo.parameters as p


class Buffer:
    def __init__(self, duration, roll=False):
        self.window = duration * p.SAMPLE_RATE
        self._data = np.zeros((p.NUM_CHANNELS, self.window ), dtype=p.PRECISION)
        self.idx = 0
        self.roll = roll

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if self.roll:
            self._data = np.roll(self._data, -data.shape[1], axis=1)
            self._data[:, -data.shape[1]:] = data

        else:
            self._data[:, self.idx:self.idx+data.shape[1]] = data
            self.idx += data.shape[1]

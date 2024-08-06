import pandas as pd
import os
import numpy as np
import importlib
from scipy import signal

# Low pass filter
sos = signal.butter(2, 5, 'lowpass', fs=250, output='sos')



def load_csv(file_path):
    # df : Elapsed Time,Isquio,Cuadriceps,GLMedio,AductorLargo,Angle
    # Load csv
    df = pd.read_csv(file_path)
    # Set dtypes
    df = df.astype(float)

    return df


def example_marcha():
    path = importlib.util.find_spec("ciervo").submodule_search_locations[0] + "/tests/data/marcha"
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".csv")]
    files.sort()
    return [load_csv(os.path.join(path, f)) for f in files]


def example_marcha_larga():
    path = importlib.util.find_spec("ciervo").submodule_search_locations[0] + "/tests/data/marcha_larga"
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".csv")]
    files.sort()
    return [load_csv(os.path.join(path, f)) for f in files]



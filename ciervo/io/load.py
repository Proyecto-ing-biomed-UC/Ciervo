import pandas as pd
import os
import numpy as np
import importlib
from scipy import signal

# Low pass filter
sos = signal.butter(2, 5, 'lowpass', fs=1000, output='sos')



def load_csv(file_path):
    # df : Elapsed Time,Isquio,Cuadriceps,GLMedio,AductorLargo,Angle
    dtypes = {
        "Elapsed Time": "str",
        "Isquio": float,
        "Cuadriceps": float,
        "GLMedio": float,
        "AductorLargo": float,
        "Angle": float,
    }

    # Load csv
    df = pd.read_csv(file_path)

    # Replace Nan.NaN with np.nan
    df = df.replace("NaN.NaN", 0)
    df = df.replace("NaN.0", 0)

    # Set dtypes
    df = df.astype(dtypes)

    # Interpolate nan values
    for muscle in df.columns[1:-1]:
        df[muscle] = np.interp(np.arange(len(df[muscle])), np.arange(len(df[muscle]))[~np.isnan(df[muscle])], df[muscle][~np.isnan(df[muscle])])






    # Set datetime
    df["Elapsed Time"] = np.linspace(0, len(df) / 1000, len(df))

    # Filter angle
    angle = np.array(df['Angle'])
    angle = np.interp(np.arange(len(angle)), np.arange(len(angle))[~np.isnan(angle)], angle[~np.isnan(angle)])
    angle = signal.sosfilt(sos, angle)
    df['Angle'] = angle

    return df


def example_marcha():
    path = importlib.util.find_spec("ciervo").submodule_search_locations[0] + "/tests/data/marcha"
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".csv")]
    files.sort()
    return [load_csv(os.path.join(path, f)) for f in files]

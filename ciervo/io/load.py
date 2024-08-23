import pandas as pd
import os


def load_csv(file_path):
    # df : Elapsed Time,Isquio,Cuadriceps,GLMedio,AductorLargo,Angle
    # Load csv
    df = pd.read_csv(file_path)
    # Set dtypes
    df = df.astype(float)
    return df


def load_data(path):
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".csv")]
    files.sort()
    return [load_csv(os.path.join(path, f)) for f in files]



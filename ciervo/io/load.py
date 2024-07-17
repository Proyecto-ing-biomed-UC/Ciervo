import pandas as pd
import os
import numpy as np


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

    # Set datetime
    df["Elapsed Time"] = np.linspace(0, len(df) / 1000, len(df))

    return df


def example_marcha():
    path = "tests/data/marcha"
    files = os.listdir(path)
    files = [f for f in files if f.endswith(".csv")]
    files.sort()
    return [load_csv(os.path.join(path, f)) for f in files]

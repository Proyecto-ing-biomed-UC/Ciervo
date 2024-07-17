from matplotlib import pyplot as plt
import pandas as pd


def emg_plot(df: pd.DataFrame) -> None:
    # df es un dataframe con las columnas Elapsed Time,Isquio,Cuadriceps,GLMedio,AductorLargo,Angle
    # Se grafican las columnas Isquio,Cuadriceps,GLMedio,AductorLargo,Angle

    fig, axs = plt.subplots(5, 1, figsize=(15, 14), sharex=True)

    for i, col in enumerate(
        ["Isquio", "Cuadriceps", "GLMedio", "AductorLargo", "Angle"]
    ):
        axs[i].plot(df["Elapsed Time"], df[col])
        axs[i].set_title(col)

    plt.show()


    

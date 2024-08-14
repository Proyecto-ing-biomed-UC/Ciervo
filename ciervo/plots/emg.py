from matplotlib import pyplot as plt
import pandas as pd


def emg_plot(df: pd.DataFrame, start: float = 0.0, duration: float = 10) -> None:
    # df es un dataframe con las columnas Elapsed Time,Isquio,Cuadriceps,GLMedio,AductorLargo,Angle
    # Por default solo grafica una ventana de 10 segundos desde el inicio.
    
    df = df[(df["Elapsed Time"] >= start) & (df["Elapsed Time"] <= start + duration)]




    columns = list(df.columns)
    # Remove elapsed time
    columns.remove("Elapsed Time")

    fig, axs = plt.subplots(len(columns), 1, figsize=(15, 14), sharex=True)    
    for i, col in enumerate(columns):
        axs[i].plot(df["Elapsed Time"], df[col])
        axs[i].set_title(col)

    plt.show()


    

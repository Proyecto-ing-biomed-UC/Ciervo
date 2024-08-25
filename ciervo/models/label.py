
from typing import Union
import pandas as pd
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
from ciervo.procesamiento import ButterLowpassFilter
import numpy as np



# data is list or dataframe
def label_data(data: Union[list, pd.DataFrame], num_fases: int = 10) -> pd.DataFrame:
    """
    Labels the data with phases based on the peaks in the 'Angle' column.
    Adds a new column 'labels' to the data with the phase labels.
    Args:
        data (Union[list, pd.DataFrame]): The data to be labeled. It can be either a list of pandas DataFrames or a single DataFrame.
        num_fases (int, optional): The number of phases to label each step. Defaults to 10.
    Returns:
        pd.DataFrame: The labeled data.
    Raises:
        None
    """
    if isinstance(data, pd.DataFrame):
        data = [data]

    low_pass = ButterLowpassFilter(20) 

    df_list = []
    for df in data:
        labels = []

        # Filtrado de los angulos para evitar picos
        df.loc[:, 'Angle'] = low_pass.apply(df['Angle'])

        # Encontrar los picos
        peaks = find_peaks(df['Angle'], height=50, distance=125, width=50)[0]


        # Iterar en cada paso para etiquetar
        for i in range(0, len(peaks)-1):    
            # Etiquetado al comienzo siempre es -1
            if i == 0:
                labels.extend([-1] * peaks[0]) 

            # Etiquetado de cada paso en fases
            temp = np.array([-1]* (peaks[i+1] - peaks[i]))
            for phase in range(num_fases):
                temp[int(len(temp)/num_fases*phase):int(len(temp)/num_fases*(phase+1))] = float(phase)
            labels.extend(temp)

        # Etiquetado al final siempre es -1
        labels.extend([-1] * (len(df['Angle']) - len(labels)))   
                    
        df['labels'] = np.array(labels)

        # Remover -1
        df = df[df.labels != -1].reset_index(drop=True)
        df_list.append(df)
    
    return df_list





if __name__ == '__main__':
    import os; os.system('clear')
    from ciervo.io.load import example_marcha_larga
    from ciervo.plots import emg_plot

    data = example_marcha_larga()[0]
    data = label_data(data, num_fases=3)
    emg_plot(data[0])
    
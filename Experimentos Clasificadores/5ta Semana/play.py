#!pip install import-ipynb
import import_ipynb

import numpy as np
from sklearn.model_selection import ParameterGrid
from ciervo.plots import emg_plot
import torch.nn as nn
from ciervo.io import load_data
from ciervo.models import label_data, train_test_split
from tqdm import tqdm

data_files = load_data('data/marcha_larga')



labeled_data = label_data(data_files, num_fases=4)


train_window, train_labels, test_window, test_labels = train_test_split(
        labeled_data,
        columna=["EMG_Isquio", "EMG_Cuadriceps", "EMG_AductorLargo"],
        window_size=125,
        test_size=0.2,
        overlap=0,
        random_state=42
    )
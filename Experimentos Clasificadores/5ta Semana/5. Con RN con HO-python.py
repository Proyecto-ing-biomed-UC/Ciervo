
import pandas
#!pip install import-ipynb
#import import_ipynb

from functions import * 
import numpy as np
from sklearn.model_selection import ParameterGrid
from ciervo.plots import emg_plot
import torch.nn as nn
from ciervo.io import load_data
from ciervo.models import label_data, train_test_split
from tqdm import tqdm

data_files = load_data('data/marcha_larga')

def evaluate_model(data_files, window_size, overlap, num_fases):
    # Cargar y preparar los datos
    labeled_data = label_data(data_files, num_fases=num_fases)
    
    # Dividir los datos en entrenamiento y prueba
    train_window, train_labels, test_window, test_labels = train_test_split(
        labeled_data,
        columna=["EMG_Isquio", "EMG_Cuadriceps", "EMG_AductorLargo"],
        window_size=window_size,
        test_size=0.2,
        overlap=overlap,
        random_state=42
    )
    # Procesar los datos
    train_data = label_data_and_features(train_window, divide=3)
    test_data = label_data_and_features(test_window, divide=3)
    
    # Seleccionar características
    train_data, test_data = sfs_selection(train_data, test_data, train_labels, n_indices=5)
    
    # Entrenar y evaluar Simple NN
    input_size = train_data.shape[1]
    hidden_size = 100
    output_size = num_fases
    learning_rate = 0.001
    num_epochs = 100
    
    model = SimpleNN(input_size, hidden_size, output_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    
    train_loader, test_tensor, test_labels_tensor = prepare_data_SimpleNN(train_data, train_labels, test_data, test_labels)
    train_model_SimpleNN(model, criterion, optimizer, train_loader, num_epochs)
    accuracy_nn = evaluate_model_SimpleNN(model, test_tensor, test_labels_tensor)
    
    return accuracy_nn

param_grid = {
    'window_size': [125,250,500],
    'overlap': [0, 50],
    'num_fases': [4, 8, 16]
}

best_accuracy = 0
best_params = {}

for params in ParameterGrid(param_grid):
    print(f"Testing with parameters: {params}")
    accuracy = evaluate_model(data_files,
        window_size=params['window_size'],
        overlap=params['overlap'],
        num_fases=params['num_fases']
    )
    
    print(f"Accuracy: {accuracy}")
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_params = params

print("Best parameters found:")
print(best_params)
print("Best accuracy achieved:")
print(best_accuracy)

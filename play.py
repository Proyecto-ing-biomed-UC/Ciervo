import os; os.system('clear')

# Ciervo
from ciervo.io import load_data
from ciervo.models import label_data, train_test_split
from ciervo.models.dataset import SpectrogramDataset
from ciervo.models.redes import GaitRNN
from ciervo.aux_tools import get_device

# Torch
from torch.utils.data import DataLoader
import lightning as L
import torch
from lightning.pytorch.callbacks.early_stopping import EarlyStopping




# Now you can use this device for your tensor operations
# Example: tensor = torch.tensor([1, 2, 3], device=device)

# PARAMS
BATCH = 16
NUM_FASES = 5
COLUMNS = ['EMG_Isquio', 'EMG_Cuadriceps', 'EMG_AductorLargo']
N_FFT = 32
NUM_EPOCHS = 300


# Device
device = get_device()
#device = 'cpu'

# Load data
data = load_data('data/marcha_larga')[0]

# label data
labeled_data = label_data(data, num_fases=NUM_FASES)

# split data
train_data, train_label,  test_data, test_label = train_test_split(labeled_data, 
                                         columna=COLUMNS,
                                         window_size=125, 
                                         random_state=42)

# Dataset
train_dataset = SpectrogramDataset(train_data, train_label, device=device, n_fft=N_FFT)
test_dataset = SpectrogramDataset(test_data, test_label, device=device, n_fft=N_FFT)

# Dataloader
train_dataloader = DataLoader(train_dataset, batch_size=BATCH, shuffle=True)
test_dataloder = DataLoader(test_dataset, batch_size=BATCH, shuffle=False)

sample, _ = next(iter(train_dataloader))


model = GaitRNN(n_classes=NUM_FASES, n_features=N_FFT // 2 + 1, n_hidden=16, n_layers=2, num_channels=len(COLUMNS)).to(device) 


## callbacks ##
# early stopping #
early_stop = EarlyStopping(monitor='loss/val', patience=10, mode='min')


# Trainer
trainer = L.Trainer(max_epochs=NUM_EPOCHS, callbacks=[early_stop])
trainer.fit(model, train_dataloader, test_dataloder)


# Test
trainer.test(model, test_dataloder)

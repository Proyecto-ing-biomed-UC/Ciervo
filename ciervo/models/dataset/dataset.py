from torch.utils.data import Dataset
from matplotlib import pyplot as plt
import torchaudio
import torch


class SpectrogramDataset(Dataset):
    
    def __init__(self, data, label, device='cpu', n_fft=16):
        self.data = data
        self.label = label
        self.device = device
        self.transform = torchaudio.transforms.Spectrogram(n_fft=n_fft)

    def __len__(self):
        return len(self.label)
    
    def __getitem__(self, idx):
        data = torch.tensor(self.data[idx]).float()
        label = torch.tensor(self.label[idx]).type(torch.LongTensor)

        W, C = data.shape
        
        # Convert to spectrogram
        spec_data = torch.stack([self.transform(data[:, c]) for c in range(C)])

        spec_data = spec_data.to(self.device)
        label = label.to(self.device)

        return spec_data, label
    
    def plot_sample(self):
        spec_data, _ = self.__getitem__(0)

        C = len(spec_data)
        fig, ax = plt.subplots(C, 1, figsize=(10, 10))
        for c in range(C):
            spec_db = torchaudio.transforms.AmplitudeToDB('power',top_db=80)(spec_data[c])
            ax[c].imshow(spec_db.numpy(), aspect='auto', origin='lower')
            
        plt.show()


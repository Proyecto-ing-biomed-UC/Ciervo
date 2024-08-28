import lightning as L
import torch.nn as nn
import torch
import torch.nn.functional as F


class GaitRNN(L.LightningModule):
    def __init__(self, n_classes, n_features, n_hidden, n_layers, num_channels):
        super().__init__()

        # Model
        self.linear = nn.Linear(num_channels, 1)
        self.lstm = nn.LSTM(n_features, n_hidden, n_layers, batch_first=True)
        self.fc = nn.Linear(n_hidden, n_classes)

    def forward(self, x):
        # N ~ batch size
        # C ~ number of channels
        # F ~ number of features
        # T ~ sequence length

        #  x ~ (N, C, F, T )
        x = x.permute(0, 3, 2, 1) # (N, T, F, C)
        x = self.linear(x) # (N, T, F, 1)
        x = x.squeeze(3) # (N, T, F)

        # rnn
        out, _ = self.lstm(x)  # (N, T, n_hidden)
        out = self.fc(out[:, -1, :] ) 
        return out

    def training_step(self, batch, batch_idx):
        x, y_target = batch
        
        # forward
        y_hat = self(x)

        # loss
        loss = F.cross_entropy(y_hat, y_target)

        # log
        self.log('loss/train', loss, prog_bar=True)
        acc = (y_hat.argmax(1) == y_target).float().mean()
        self.log('acc/train', acc, prog_bar=True)

        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y_target = batch

        # forward
        y_hat = self(x)

        # loss
        loss = F.cross_entropy(y_hat, y_target)

        # log
        self.log('loss/val', loss, prog_bar=True)
        acc = (y_hat.argmax(1) == y_target).float().mean()
        self.log('acc/val', acc, prog_bar=True)

        return loss
    
    def test_step(self, batch, batch_idx):
        x, y_target = batch

        # forward
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y_target)

        # log
        self.log('loss/test', loss)
        acc = (y_hat.argmax(1) == y_target).float().mean()
        self.log('acc/test', acc)

        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.01)
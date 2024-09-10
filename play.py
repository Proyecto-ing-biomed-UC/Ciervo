import os; os.system('clear')
import numpy as np
from matplotlib import pyplot as plt

a = np.load('recordings/test_contraction.npy')

print(a.shape) #( C, T)
C, T = a.shape

fig, ax = plt.subplots(C, 1)

for i in range(a.shape[0]):
    ax[i].plot(a[i, :])

plt.show()

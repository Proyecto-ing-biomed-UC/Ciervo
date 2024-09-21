import numpy as np
import matplotlib.pyplot as plt

my_data = np.genfromtxt('./data/angle.csv', delimiter=',')

print(my_data[1:])

plt.plot(my_data)
plt.show()
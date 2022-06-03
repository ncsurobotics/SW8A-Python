from acoustics import Acoustics
import numpy as np
import matplotlib.pyplot as plt


# create fake data
tstep = 1

t = np.arange(10)
a = np.cos(2*np.pi*1*tstep*t)
b = np.cos(2*np.pi*1*tstep*t - 0.5*np.pi)

plt.plot(t, a, t, b, 'r')
plt.savefig('img.png')
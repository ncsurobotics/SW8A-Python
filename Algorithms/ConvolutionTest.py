import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# def conv(function, impulse):
#     filtered = np.zeros(len(function) + len(impulse) - 1)
#     for i in range(len(function)):
#         for j in range(len(impulse)):
#             filtered[i+j] = filtered[i+j] + (function[i] * impulse[j])
#     return filtered
#
#
#
# out = conv(sig, win)
#

data = []
data = np.genfromtxt("sincos.csv", delimiter=",")

sig = data[0]
win = data[1]
filtered = signal.convolve(sig, win, mode='same', method='fft')
fig, (ax_orig, ax_win, ax_filt) = plt.subplots(3, 1, sharex=True)
ax_orig.plot(sig)
ax_orig.set_title('Original pulse')
ax_orig.margins(0, 0.1)
ax_win.plot(win)
ax_win.set_title('Filter impulse response')
ax_win.margins(0, 0.1)
ax_filt.plot(filtered)
ax_filt.set_title('Filtered signal')
ax_filt.margins(0, 0.1)
fig.tight_layout()
plt.show()

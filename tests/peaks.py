import numpy as np
from scipy import fft, signal

# extract data from pool test csv
# column 0: time (ns), column 1: mV
data = []
data = np.genfromtxt("Far_Range_0.csv", delimiter=",", skip_header=1) # real data
t, v = data[:, 0], data[:, 1]

tstep = t[1]*10**-9   # get time step in seconds

# fft
# uses scipy rfft function, which returns only positive frequencies
vfourier = fft.rfft(v)
mags = np.abs(vfourier)
f = fft.rfftfreq(v.size, d=tstep) # frequency axis

# get peaks using scipy find_peaks 
peaks, _ = signal.find_peaks(mags, height=0.25*mags.max(), distance=1000)
print('Peaks are: ' , peaks)
peak_freqs = f[peaks]
print('Frequencies are:' , peak_freqs)
peak_mags = mags[peaks]
print('Magnitudes are:' , (peak_mags))

# print dominant frequency
dominant_freq = peak_freqs[peak_mags.argmax()]
print('Dominant frequency: ', dominant_freq)
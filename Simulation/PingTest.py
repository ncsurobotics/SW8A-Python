import numpy as np
from Simulation import Ping
from Simulation import Pinger
import matplotlib.pyplot as plt

end = 4e-3
freq = 25000
amp = 1
sample = 1.24e-6
loc = (0, 0, 0)
noise_mean = 0.25
noise_var = 0.25

p = Ping(end, freq, amp, sample)
p.generate_ping()

pinger = Pinger(loc, p)

t = p.time

pinger.introduce_noise(noise_mean, noise_var)
signal = p.ping_values

print(signal)

plt.plot(t, signal)
plt.show()

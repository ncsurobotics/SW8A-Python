import numpy as np
import math
from Simulation import Ping
from Simulation import Pinger
from Simulation import Hydrophone
import matplotlib.pyplot as plt

speed_of_sound = 1480
end = 4e-3
freq = 25000
amp = 1
sample = 1.24e-6
pinger_loc = (0, 0, 0)
noise_mean = 0
noise_var = 0
dead_time = 500

hydrophone1_loc = (0,0,0)
hydrophone2_loc = (0,0,0)
hydrophone3_loc = (0,0,0)
hydrophone4_loc = (0,1,1)

p = Ping(end, freq, amp, sample)
pinger = Pinger(pinger_loc, p)

p.generate_ping()
p.add_dead_time(dead_time)
pinger.introduce_noise(noise_mean, noise_var)
signal = p.ping_values
t = p.time

data = np.vstack((t, signal))
print(data)

#known error - data turns into a 1d array at some point, should have both time and data

h1 = Hydrophone(hydrophone1_loc, data)
h2 = Hydrophone(hydrophone2_loc, data)
h3 = Hydrophone(hydrophone3_loc, data)
h4 = Hydrophone(hydrophone4_loc, data)

distance1 = math.sqrt((hydrophone1_loc[0] - pinger_loc[0])**2 + (hydrophone1_loc[1] - pinger_loc[1])**2 + (hydrophone1_loc[2] - pinger_loc[2])**2)
distance2 = math.sqrt((hydrophone2_loc[0] - pinger_loc[0])**2 + (hydrophone2_loc[1] - pinger_loc[1])**2 + (hydrophone2_loc[2] - pinger_loc[2])**2)
distance3 = math.sqrt((hydrophone3_loc[0] - pinger_loc[0])**2 + (hydrophone3_loc[1] - pinger_loc[1])**2 + (hydrophone3_loc[2] - pinger_loc[2])**2)
distance4 = math.sqrt((hydrophone4_loc[0] - pinger_loc[0])**2 + (hydrophone4_loc[1] - pinger_loc[1])**2 + (hydrophone4_loc[2] - pinger_loc[2])**2)

time_shift1 = distance1/speed_of_sound;
time_shift2 = distance2/speed_of_sound;
time_shift3 = distance3/speed_of_sound;
time_shift4 = distance4/speed_of_sound;

print(time_shift1)
print(time_shift2)
print(time_shift3)
print(time_shift4)

time_shift1 = round((distance1/speed_of_sound)/sample);
time_shift2 = round((distance2/speed_of_sound)/sample);
time_shift3 = round((distance3/speed_of_sound)/sample);
time_shift4 = round((distance4/speed_of_sound)/sample);

h1.adjust_delay(time_shift1)
h2.adjust_delay(time_shift2)
h3.adjust_delay(time_shift3)
h4.adjust_delay(time_shift4)

plt.plot(h1.received_data[0], h1.received_data[1])
plt.plot(h2.received_data[0], h2.received_data[1])
plt.plot(h3.received_data[0], h3.received_data[1])
plt.plot(h4.received_data[0], h4.received_data[1])
plt.show()

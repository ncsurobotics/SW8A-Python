import numpy as np

class Ping(object):
    time = [0]
    ping_values = [0]
    # time is a vector - pings are a function of time
    # end_time - length of the ping, will always start at time = 0
    # frequency - frequency of the ping, between 25000 40000
    # intensity - amplitude of the ping
    def __init__(self, end_time, frequency, intensity, sampling_period):
        self.end_time = end_time
        self.frequency = frequency
        self.intensity = intensity
        self.sampling_period = sampling_period

    #setters        
    def set_end_time(self, end_time):
        self.end_time = end_time

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_intensity(self, intensity):
        self.intensity = intensity

    def set_sampling_period(self, sampling_period):
        self.sampling_period = sampling_period

    #Generates the time and pin_values arrays
    def generate_ping(self):
        self.time = np.arange(0, self.end_time, self.sampling_period)
        self.ping_values = self.intensity * np.sin(self.time * self.frequency * 2 * np.pi)

    def add_noise(self, noise):
        self.ping_values = np.add(self.ping_values, noise)
    
class Pinger(object):
    # location is a vector - (x,y,z) coordinates of the pinger
    # shittiness is a list of parameters used to create noise
    # ping is object (see above)
    def __init__(self, location, ping):
        self.location = location
        self.ping = ping or Ping(0, 0, 0, 0)
    
    #setters
    def set_location(self,location):
        self.location = location
        
    def set_ping(self, ping):
        self.ping = ping

    def introduce_noise(self, mean, var):
        noise = np.random.normal(mean, var, size = len(self.ping.time))
        self.ping.add_noise(noise)

class Hydrophone(object):
    # location is a vector - (x,y,z) coordinates of the hydrophone
    # recieved_data is a vector of the data and the time it was read
    # in the same format as when we do actual tests
    def __init__(self, location, received_data):
        self.location = location
        self.received_data = received_data

    #setters
    def set_location(self, location):
        self.location = location
        
    def set_size(self,size):
        self.size = size
        
    def set_received_data(self, received_data):
        self.received_data = received_data


class Simulation(object):
    def __init__(self, place_holder):
        self.place_holder = place_holder

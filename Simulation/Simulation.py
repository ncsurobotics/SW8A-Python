import numpy as np

class Ping(object):
    def __init__(self, time, values):
        self.time = time
        self.values = values

    #setters
    
        
    def set_values(self, values):
        self.values = values
    
class Pinger(object):
    def __init__(self, location, shittiness, ping = None):
        self.location = location
        self.shittiness = shittiness
        self.ping = ping or Ping(0, 0, 0, 0, [0])
        noise = np.random.normal(shittiness[0],shittiness[1], size = len(ping.values))
        self.ping.set_values(np.add(self.ping.values,noise))
        
    
    #setters
    def set_location(self,location):
        self.location = location
       
    def set_shittiness(self,shittiness):
        self.shittiness = shittiness
        
    def set_ping(self, ping):
        self.ping = ping

class Hydrophone(object):
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
    return 0
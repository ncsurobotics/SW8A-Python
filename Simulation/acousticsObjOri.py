
class Acoustics:

    
    def __init__(self, run_name, num_channels, delta_x, delta_z):
        self.pitch = 0;
        self.yaw = 0;
        self.channels = [[]*num_channels]
        self.run_name = run_name
        self.delta_x = delta_x
        self.delta_z = delta_z
        self.delta_t = 0;
    
    def initialize(self):
        '''
            Find a way to write this in such a way that it is a loop instead of brute.
            Potentially allows code to be somewhat reusable under more hydrophones
        '''
        return 0
        
    def data_sample(self):
        '''
            Find a way to write this in such a way that it is a loop instead of brute.
            Potentially allows code to be somewhat reusable under more hydrophones
        '''
        return 0

    def time_difference(channel_one, channel_two):
        '''
            Convolutional function to determine the delta t value based on cross correlation
        '''
        
        cross_correlation = [0]
        
        
        k = len(channel_one)
        i = len(channel_two)
        
        for n in range(0, k + i - 1):
            cross_correlation[n] = 0
            for m in range(0,k - 1):
                if(m + n - (k - 1) < 0):
                    cross_correlation[n] = 0
                else:
                    cross_correlation[n] = cross_correlation[n] + (channel_two[m] * channel_one[n + m - (k - 1)])
            cross_correlation.append(0)
        
        return cross_correlation.index(max(cross_correlation))
        
    def c_val(delta_a, delta_t):
        d = delta_t * 1480  
        c = (d**2) / ( (delta_a**2) - d**2)
        return c;
    
    def pitch_yaw(self,C1,C2):
        arg1 = math.sqrt( (C1 + 1) / (C2 + C1 * C2) )
        arg2 = math.sqrt( (C1 + C1 * C2) / (1 - C1 * C2) )
        
        self.pitch = math.atan(arg1)
        self.yaw = math.atan(arg2)
        
        

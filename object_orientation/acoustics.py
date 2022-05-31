import math
import ctypes
from picosdk.functions import adc2mV, assert_pico_ok
import numpy as np
from scipy import signal, fft 
import matplotlib.pyplot as plt
import csv
import os
from datetime import date

class Acoustics:

    def __init__(self, num_channels = 4, delta_x = 0, delta_z = 0):
        self.init_run_attributes()
        self.init_channels()
        self.init_trigger()
        self.init_buffer_attributes()
        self.init_device_variables()

        self.pitch = 0;
        self.yaw = 0;
        self.delta_x = delta_x
        self.delta_z = delta_z
        self.delta_t = 0;

        self.ready = ctypes.c_int16(0)
        self.check = ctypes.c_int16(0)
        self.overflow = ctypes.c_int16() # create overflow location
        self.C_MAX_SAMPLES = ctypes.c_int32(self.MAX_SAMPLES) # create converted type maxSamples
        self.plotted = False

        self.channels = []
        self.buffer_maxes = []
        self.buffer_mins = []
        for i in range(0, num_channels):
            self.channels.append([])
            self.buffer_maxes.append( (ctypes.c_int16 * self.MAX_SAMPLES)() )
            self.buffer_mins.append( (ctypes.c_int16 * self.MAX_SAMPLES)() )

    def initialize(self, trigger_channel = 0, trigger_frequency = 9.98e7, threshold = 0.5, auto_trigger = 0, delay = 0):
        '''Sets up the physical PicoScope interface.'''

        self.plotted = False

        self.open_unit()
        self.open_channels()
        self.set_sample_length(trigger_frequency)
        self.set_trigger(trigger_channel, threshold, auto_trigger, delay)
        self.buffers()

    def run(self, run_name):
        '''Collects samples from the PicoScope.'''

        self.run_name = run_name
        self.block()
        self.get_values()
        self.adc_to_mV()

    def end(self):
        ''' Properly shuts down and disconnects the PicoScope. '''

        self.stop()
        self.close()

    def c_val(self, delta_a, delta_t):
        d = delta_t * 1480
        c = (d**2) / ( (delta_a**2) - d**2)

    def get_time(self):
        ''' Returns the linearly spaced time.
            Only works properly after run(). '''

        return np.linspace(0, (self.C_MAX_SAMPLES.value) * self.time_interval_ns.value, self.C_MAX_SAMPLES.value)

    def plot(self):
        ''' Creates a plot for all channels.
            Used by show_plot() and write_plot(). '''

        if self.plotted:
            return
        time = self.get_time()
        fig, axs = plt.subplots(len(self.adc_2mV_maxes))
        for i in range(0, len(self.adc_2mV_maxes)):
            axs[i].plot(time, self.adc_2mV_maxes[i][:])
            axs[i].title.set_text("Channel " + str(i))
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        self.plotted = True

    def show_plot(self):
        ''' Displays a plot in an X11 frame. '''
        self.plot()
        plt.show()

    def write_plot(self):
        ''' Writes a plot image to a png. '''
        self.plot()
        if not os.path.exists(str(date.today())):
            os.mkdir(str(date.today()))
        plt.savefig(str(date.today()) + "/" + str(self.run_name) + ".png")

    def write_csv(self):
        ''' Writes the data as a csv. '''
        if not os.path.exists(str(date.today())):
            os.mkdir(str(date.today()))
        titles = ["time"]
        for i in range(0, len(self.adc_2mV_maxes)):
            titles.append("Channel_" + str(i))

        with open(str(date.today()) + "/" + str(self.run_name) + ".csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerow(titles)
            time = self.get_time()
            for index in len(time):
                writer.writerow([ time[index] ] + \
                        [ adc_max[index] for adc_max in adc_2mV_maxes ])

    def fourier(self, channel, tstep):
        '''
            returns dominant frequency of ping
        '''
        
        mag = np.abs(fft.rfft(channel)) # rfft - positive frequencies only
        f = fft.rfftfreq(channel_transform.size, d=tstep) # frequency axis
        
        mag = np.abs(channel_transform)
        findex = channel_transform.index(max(mag))
        
        return f[findex]

    def time_difference(self, channel_one, channel_two):
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
                    cross_correlation[n] = cross_correlation[n] + 0
                else:
                    cross_correlation[n] = cross_correlation[n] + (channel_two[m] * channel_one[n + m - (k - 1)])
            cross_correlation.append(0)

        return cross_correlation.index(max(cross_correlation)) # returns index NOT time 
        
    def time_difference_2(self, channel_one, channel_two):
        # tdoa from scipy cross correlation function
        # todo: try fft based cross correlation 
        
        cross_correlation = signal.correlate(channel_one, channel_two, mode='full', method='auto')
        return cross_correlation.index(max(cross_correlation))

    def pitch_yaw(self,C1,C2):
        arg1 = math.sqrt( (C1 + 1) / (C2 + C1 * C2) )
        arg2 = math.sqrt( (C1 + C1 * C2) / (1 - C1 * C2) )

        self.pitch = math.atan(arg1)
        self.yaw = math.atan(arg2)

    # Virtual functions

    def init_run_attributes(self, period):
        raise NotImplementedError()

    def init_channels(self):
        raise NotImplementedError()

    def init_trigger(self):
        raise NotImplementedError()

    def init_buffer_attributes(self):
        raise NotImplementedError()

    def init_device_variables(self):
        raise NotImplementedError()

    def open_unit(self):
        raise NotImplementedError()

    def set_sample_length(self, trigger_frequency):
        raise NotImplementedError()

    def open_channels(self):
        '''Creates a connection for each channel.

        Goes from 0 to one less than channels size.'''
        raise NotImplementedError()

    def set_trigger(self, trigger_channel = 0, threshold = 0.5, auto_trigger = 0, delay = 0):
        '''Sets a sampling threshold.

        Parameters:
            trigger_channel: The channel number to watch
            threshold: The minimum signal voltage to trigger
            delay: milliseconds to delay after trigger
            auto_trigger: milliseconds to trigger without passing threshold
        '''
        raise NotImplementedError()

    def volts_to_adc(threshold):
        '''Converts a target voltage to device ADC

        ADC is threshold / (ADC_counts = 32767) * (range = 2)
        '''
        return math.ceil((threshold / 2) * 32767)

    def buffers(self):
        '''Creates buffers to capture data.'''
        raise NotImplementedError()

    def block(self):
        raise NotImplementedError()

    def get_values():
        self.adc_2mV_maxes = []
        for i in range(0, len(self.channels)):
            self.adc_2mV_maxes.append(adc2mV(self.buffer_maxes[i], self.RANGE, self.MAX_ADC))

    def stop(self):
        ''' Stops the PicoScope. '''
        raise NotImplementedError()

    def close(self):
        ''' Closes the PicoScope. '''
        raise NotImplementedError()

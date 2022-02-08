import math
import ctypes
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

class Acoustics:

    def __init__(self, run_name, num_channels, delta_x, delta_z):
        self.pitch = 0;
        self.yaw = 0;
        self.channels = [[]*num_channels]
        self.run_name = run_name
        self.delta_x = delta_x
        self.delta_z = delta_z
        self.delta_t = 0;

        # Device variables
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.time_interval_ns = ctypes.c_float()
        self.returned_max_samples = ctypes.c_int32()
        self.oversample = ctypes.c_int16(1)

        # Run attributes
        self.PRE_TRIGGER_SAMPLES = 20000
        self.POST_TRIGGER_SAMPLES = 60000
        self.MAX_SAMPLES = self.PRE_TRIGGER_SAMPLES + self.POST_TRIGGER_SAMPLES
        self.TIMEBASE = 64 # No idea what period this is
        self.TIME_INDISPOSED = None # milliseconds
        self.SEGMENT_INDEX = 0
        self.LP_READY = None # uses ps4000aIsReady, not ps4000aBlockReady
        self.P_PARAMETER = None

        # Channel attributes
        self.COUPLING_TYPE = 1 # PS4000a_DC
        self.RANGE = 7 # PS4000a_2V
        self.ANALOG_OFFSET = 0 # in volts
        # Channel/Trigger attributes
        self.ENABLED = 1

        # Trigger attributes
        self.THRESHOLD = 8200 # ADC counts
        self.DIRECTION = 2 # PS4000a_RISING
        self.DELAY = 0 # seconds
        self.AUTO_TRIGGER = 00 # milliseconds

        # Buffer Attributes
        self.MODE = 0 # PS4000A_RATIO_MODE_NONE
        self.START_INDEX = 0
        self.DOWNSAMPLE_RATIO = 0
        self.DOWNSAMPLE_RATIO_MODE = 0 # PS4000a_RATIO_MODE_NONE
        self.MAX_ADC = ctypes.c_int16(32767) # max ADC count value
        self.buffer_max = (ctypes.c_int16 * self.MAX_SAMPLES)()
        self.adc_2mV_maxes = []

        # Extra ctypes
        self.ready = ctypes.c_int16(0)
        self.check = ctypes.c_int16(0)
        self.overflow = ctypes.c_int16() # create overflow location
        self.C_MAX_SAMPLES = ctypes.c_int32(self.MAX_SAMPLES) # create converted type maxSamples
        self.buffer_min = (ctypes.c_int16 * self.MAX_SAMPLES)()

    def initialize(self):
        '''Sets up the physical PicoScope interface.'''

        self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.chandle), None)
        try:
            assert_pico_ok(self.status["openunit"])
        except:
            power_status = self.status["openunit"]
            if power_status == 286:
                self.status["changePowerSource"] = \
                        ps.ps4000aChangePowerSource(self.chandle, power_status)
            else:
                raise
            assert_pico_ok(self.status["changePowerSource"])
        self.open_channels()
        self.set_trigger(1)

    def open_channels(self):
        '''Creates a connection for each channel.

        Goes from 0 to one less than channels size.'''

        for i in range(0, self.channels.__len__() - 1):
            self.status["setCh" + str(i)] = \
                ps.ps4000aSetChannel(self.chandle, i, self.ENABLED, \
                self.COUPLING_TYPE, self.RANGE, self.ANALOG_OFFSET)
            i -= 1

    def set_trigger(self, i):
        '''Sets a sampling threshold.

        Parameters:
            i: The channel number to watch
        '''

        self.status["trigger"] = ps.ps4000aSetSimpleTrigger(self.chandle, self.ENABLED, \
                i, self.THRESHOLD, self.DIRECTION, self.DELAY, self.AUTO_TRIGGER)
        assert_pico_ok(self.status["trigger"])


    def time_difference(self, channel_one, channel_two):
        '''
            Convolutional function to determine the delta t value based on cross correlation
        '''

        cross_correlation = [0]


        k = len(channel_one)
        i = len(channel_two)

        for n in RANGE(0, k + i - 1):
            cross_correlation[n] = 0
            for m in RANGE(0,k - 1):
                if(m + n - (k - 1) < 0):
                    cross_correlation[n] = cross_correlation[n] + 0
                else:
                    cross_correlation[n] = cross_correlation[n] + (channel_two[m] * channel_one[n + m - (k - 1)])
            cross_correlation.append(0)

        return cross_correlation.index(max(cross_correlation))

    def run(self):
        '''Collects samples from the PicoScope.'''

        # Timebase information
        self.status["getTimebase2"] = ps.ps4000aGetTimebase2(self.chandle, self.TIMEBASE, \
                self.MAX_SAMPLES, ctypes.byref(self.time_interval_ns), \
                ctypes.byref(self.returned_max_samples), 0)
        assert_pico_ok(self.status["getTimebase2"])

        # Block capture
        self.status["runBlock"] = ps.ps4000aRunBlock(self.chandle, self.PRE_TRIGGER_SAMPLES, \
                self.POST_TRIGGER_SAMPLES, self.TIMEBASE, self.TIME_INDISPOSED, \
                self.SEGMENT_INDEX, self.LP_READY, self.P_PARAMETER)
        assert_pico_ok(self.status["runBlock"])

        # Wait for data collection to finish
        while self.ready.value == self.check.value:
            self.status["isReady"] = ps.ps4000aIsReady(self.chandle, ctypes.byref(self.ready))

        self.buffers()

        # Retrieve buffer data
        self.status["getValues"] = ps.ps4000aGetValues(self.chandle, self.START_INDEX, \
                ctypes.byref(self.C_MAX_SAMPLES), self.DOWNSAMPLE_RATIO, self.DOWNSAMPLE_RATIO_MODE, \
                0, ctypes.byref(self.overflow))
        assert_pico_ok(self.status["getValues"])

        # ADC counts to mV
        for i in range(0, self.channels.__len__() - 1):
            self.adc_2mV_maxes[i] = adc2mV(self.buffer_max, self.RANGE, self.MAX_ADC)
            i -= 1

    def buffers(self):
        '''Creates buffers to capture data.'''

        for i in range(0, self.channels.__len__() - 1):
            self.status["setDataBuffers" + str(i)] = ps.ps4000aSetDataBuffers(self.chandle, i, \
                    ctypes.byref(self.buffer_max), ctypes.byref(self.buffer_min), self.MAX_SAMPLES, self.SEGMENT_INDEX, self.MODE)
            assert_pico_ok(self.status["setDataBuffers" + str(i)])
            i -= 1

    def c_val(self, delta_a, delta_t):
        d = delta_t * 1480
        c = (d**2) / ( (delta_a**2) - d**2)

    def pitch_yaw(self,C1,C2):
        arg1 = math.sqrt( (C1 + 1) / (C2 + C1 * C2) )
        arg2 = math.sqrt( (C1 + C1 * C2) / (1 - C1 * C2) )

        self.pitch = math.atan(arg1)
        self.yaw = math.atan(arg2)

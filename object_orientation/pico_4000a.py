from acoustics import *
from picosdk.ps4000a import ps4000a as ps

class Pico_4000a(Acoustics):

    def __init__(self, num_channels = 4, delta_x = 0, delta_z = 0):
        super().__init__(num_channels, delta_x, delta_z)

    def init_run_attributes(self):
        self.PRE_TRIGGER_SAMPLES = 20000
        self.POST_TRIGGER_SAMPLES = 60000
        self.MAX_SAMPLES = self.PRE_TRIGGER_SAMPLES + self.POST_TRIGGER_SAMPLES
        self.TIME_INDISPOSED = None # milliseconds
        self.SEGMENT_INDEX = 0
        self.LP_READY = None # uses ps4000aIsReady, not ps4000aBlockReady
        self.P_PARAMETER = None

    def init_channels(self):
        self.COUPLING_TYPE = 1 # PS4000a_DC
        self.RANGE = 7 # PS4000a_2V, 2V range
        self.ANALOG_OFFSET = 0 # in volts
        self.ENABLED = 1

    def init_trigger(self):
        self.DIRECTION = 2 # PS4000a_RISING

    def init_buffer_attributes(self):
        self.MODE = 0 # PS4000A_RATIO_MODE_NONE
        self.START_INDEX = 0
        self.DOWNSAMPLE_RATIO = 0
        self.DOWNSAMPLE_RATIO_MODE = 0 # PS4000a_RATIO_MODE_NONE
        self.MAX_ADC = ctypes.c_int16(32767) # max ADC count value

    def init_device_variables(self):
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.time_interval_ns = ctypes.c_float()
        self.returned_max_samples = ctypes.c_int32()

    #def set_sample_length(self, frequency):
    def set_sample_length(self, length):
        # sample interval = 12.5 ns * (TIMEBASE + 1)
        # sample freq = 80 MHz / (TIMEBASE + 1)
        # sample length = (sample interval) * MAX_SAMPLES
        #self.TIMEBASE = math.floor(80e6 / frequency)
        #self.TIMEBASE = math.floor((length - (12.5e-9 * self.MAX_SAMPLES) ) / 12.5e-9)
        self.TIMEBASE = math.floor(length / (12.5e-9 * self.MAX_SAMPLES)) - 1
        self.status["getTimebase2"] = ps.ps4000aGetTimebase2(self.chandle, self.TIMEBASE, \
                self.MAX_SAMPLES, ctypes.byref(self.time_interval_ns), \
                ctypes.byref(self.returned_max_samples), 0)
        assert_pico_ok(self.status["getTimebase2"])

    def open_unit(self):
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

    def open_channels(self):
        '''Creates a connection for each channel.

        Goes from 0 to one less than channels size.'''
        for i in range(0, len(self.channels)):
            self.status["setCh" + str(i)] = \
                ps.ps4000aSetChannel(self.chandle, i, self.ENABLED, \
                self.COUPLING_TYPE, self.RANGE, self.ANALOG_OFFSET)

    def set_trigger(self, trigger_channel = 0, threshold = 0.5, auto_trigger = 0, delay = 0):
        '''Sets a sampling threshold.

        Parameters:
            trigger_channel: The channel number to watch
            threshold: The minimum signal voltage to trigger
            delay: milliseconds to delay after trigger
            auto_trigger: milliseconds to trigger without passing threshold
        '''
        self.status["trigger"] = ps.ps4000aSetSimpleTrigger(self.chandle, self.ENABLED, \
                trigger_channel, super().volts_to_adc(threshold), self.DIRECTION, delay, auto_trigger)

    def buffers(self):
        '''Creates buffers to capture data.'''
        for i in range(0, len(self.channels)):
            self.status["setDataBuffers" + str(i)] = ps.ps4000aSetDataBuffers(self.chandle, i, \
                    ctypes.byref(self.buffer_maxes[i]), ctypes.byref(self.buffer_mins[i]), \
                    self.MAX_SAMPLES, self.SEGMENT_INDEX, self.MODE)
            assert_pico_ok(self.status["setDataBuffers" + str(i)])

    def block(self):
        self.status["runBlock"] = ps.ps4000aRunBlock(self.chandle, self.PRE_TRIGGER_SAMPLES, \
                self.POST_TRIGGER_SAMPLES, self.TIMEBASE, self.TIME_INDISPOSED, \
                self.SEGMENT_INDEX, self.LP_READY, self.P_PARAMETER)
        assert_pico_ok(self.status["runBlock"])

        self.ready.value = 0
        while self.ready.value == self.check.value:
            self.status["isReady"] = ps.ps4000aIsReady(self.chandle, ctypes.byref(self.ready))

    def values_call(self):
        self.status["getValues"] = ps.ps4000aGetValues(self.chandle, self.START_INDEX, \
                ctypes.byref(self.C_MAX_SAMPLES), self.DOWNSAMPLE_RATIO, self.DOWNSAMPLE_RATIO_MODE, \
                0, ctypes.byref(self.overflow))

    def stop(self):
        ''' Stops the PicoScope. '''
        self.status["stop"] = ps.ps4000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

    def close(self):
        ''' Closes the PicoScope. '''
        self.status["close"] = ps.ps4000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])

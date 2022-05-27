from acoustics import *
from picosdk.ps2000a import ps2000a as ps

class Pico_2000a(Acoustics):

    def init_run_attributes(self):
        self.PRE_TRIGGER_SAMPLES = 3500
        self.POST_TRIGGER_SAMPLES = 8500
        self.MAX_SAMPLES = self.PRE_TRIGGER_SAMPLES + self.POST_TRIGGER_SAMPLES
        self.TIME_INDISPOSED = None # milliseconds
        self.SEGMENT_INDEX = 0
        self.LP_READY = None # uses ps2000aIsReady, not ps2000aBlockReady
        self.P_PARAMETER = None

    def init_channels(self):
        self.COUPLING_TYPE = 1 # PS2000a_DC
        self.RANGE = 7 # PS2000a_2V, 2V range
        self.ANALOG_OFFSET = 0 # in volts
        self.ENABLED = 1

    def init_trigger(self):
        self.DIRECTION = 2 # PS2000a_RISING

    def init_buffer_attributes(self):
        self.MODE = 0 # PS2000A_RATIO_MODE_NONE
        self.START_INDEX = 0
        self.DOWNSAMPLE_RATIO = 0
        self.DOWNSAMPLE_RATIO_MODE = 0 # PS2000a_RATIO_MODE_NONE
        self.MAX_ADC = ctypes.c_int16(32767) # max ADC count value

    def init_device_variables(self):
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.time_interval_ns = ctypes.c_float()
        self.returned_max_samples = ctypes.c_int32()
        self.OVERSAMPLE = ctypes.c_int16(0) # Not used, but in API

    def set_sample_length(self, frequency):
        # sample interval = (TIMEBASE - 2) / 62,500,000 seconds
        # sample freq = 62,500,000 / (TIMEBASE - 2)
        # sample length = (sample interval) * MAX_SAMPLES
        self.TIMEBASE = math.ceil(62.5e6 / frequency) + 2
        self.status["getTimebase2"] = ps.ps2000aGetTimebase2(self.chandle, self.TIMEBASE, \
                self.MAX_SAMPLES, ctypes.byref(self.time_interval_ns), \
                self.OVERSAMPLE, ctypes.byref(self.returned_max_samples), 0)
        assert_pico_ok(self.status["getTimebase2"])

    def open_unit(self):
        self.status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(self.chandle), None)
        try:
            assert_pico_ok(self.status["openunit"])
        except:
            power_status = self.status["openunit"]
            if power_status == 286:
                self.status["changePowerSource"] = \
                        ps.ps2000aChangePowerSource(self.chandle, power_status)
            else:
                raise
            assert_pico_ok(self.status["changePowerSource"])

    def open_channels(self):
        '''Creates a connection for each channel.

        Goes from 0 to one less than channels size.'''
        for i in range(0, len(super().channels)):
            self.status["setCh" + str(i)] = \
                ps.ps2000aSetChannel(self.chandle, i, self.ENABLED, \
                self.COUPLING_TYPE, self.RANGE, self.ANALOG_OFFSET)

    def set_trigger(self, trigger_channel = 0, threshold = 0.5, auto_trigger = 0, delay = 0):
        '''Sets a sampling threshold.

        Parameters:
            trigger_channel: The channel number to watch
            threshold: The minimum signal voltage to trigger
            delay: milliseconds to delay after trigger
            auto_trigger: milliseconds to trigger without passing threshold
        '''
        self.status["trigger"] = ps.ps2000aSetSimpleTrigger(self.chandle, self.ENABLED, \
                i, volts_to_adc(threshold), self.DIRECTION, delay, auto_trigger)

    def buffers(self):
        '''Creates buffers to capture data.'''
        for i in range(0, len(super().channels)):
            self.status["setDataBuffers" + str(i)] = ps.ps2000aSetDataBuffers(self.chandle, i, \
                    ctypes.byref(super().buffer_maxes[i]), ctypes.byref(super().buffer_mins[i]), self.MAX_SAMPLES, self.SEGMENT_INDEX, self.MODE)
            assert_pico_ok(self.status["setDataBuffers" + str(i)])

    def block(self):
        self.status["runBlock"] = ps.ps2000aRunBlock(self.chandle, self.PRE_TRIGGER_SAMPLES, \
                self.POST_TRIGGER_SAMPLES, self.TIMEBASE, self.OVERSAMPLE, self.TIME_INDISPOSED, \
                self.SEGMENT_INDEX, self.LP_READY, self.P_PARAMETER)
        assert_pico_ok(self.status["runBlock"])

        super().ready.value = 0
        while super().ready.value == super().check.value:
            self.status["isReady"] = ps.ps2000aIsReady(self.chandle, ctypes.byref(super().ready))

        raise NotImplementedError()

    def stop(self):
        ''' Stops the PicoScope. '''
        ps.ps400aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

    def close(self):
        ''' Closes the PicoScope. '''
        ps.ps2000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])

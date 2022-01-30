import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import csv


class Acoustics:
    noise_length = 100
    ping_detect = 0.025

    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}

    # Set number of pre and post trigger samples to be collected
    preTriggerSamples = 20000
    postTriggerSamples = 60000
    maxSamples = preTriggerSamples + postTriggerSamples

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = (ctypes.c_int16 * maxSamples)()
    bufferAMin = (ctypes.c_int16 * maxSamples)()  # used for downsampling which isn't in the scope of this example
    bufferBMax = (ctypes.c_int16 * maxSamples)()
    bufferBMin = (ctypes.c_int16 * maxSamples)()  # used for downsampling which isn't in the scope of this example
    bufferCMax = (ctypes.c_int16 * maxSamples)()
    bufferCMin = (ctypes.c_int16 * maxSamples)()  # used for downsampling which isn't in the scope of this example
    bufferDMax = (ctypes.c_int16 * maxSamples)()
    bufferDMin = (ctypes.c_int16 * maxSamples)()  # used for downsampling which isn't in the scope of this example

    # create overflow loaction
    overflow = ctypes.c_int16()
    # create converted type maxSamples
    cmaxSamples = ctypes.c_int32(maxSamples)

    def __init__(self):
        self.open_4000(self)
        self.set_up_channels(self)
        self.set_trigger(self)
        self.set_timebase(self)
        self.run_block_capture(self)
        self.ready(self)
        self.set_buffer_location(self)

    def open_4000(self):
        self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.chandle), None)

        try:
            assert_pico_ok(self.status["openunit"])
        except:

            powerStatus = self.status["openunit"]

            if powerStatus == 286:
                self.status["changePowerSource"] = ps.ps4000aChangePowerSource(self.chandle, powerStatus)
            else:
                raise

            assert_pico_ok(self.status["changePowerSource"])

    # Set up channels
    # handle = chandle
    # channel = PS4000a_CHANNEL_A = 0, PS4000a_CHANNEL_B = 1, ..., PS4000a_CHANNEL_H = 1
    # enabled = 1 disabled = 0
    # coupling type = PS4000a_DC = 1
    # range = PS4000a_2V = 7
    # analogOffset = 0 V
    def set_up_channels(self):
        # Set up channel A
        chARange = 8
        self.status["setChA"] = ps.ps4000aSetChannel(self.chandle, 0, 1, 1, chARange, 0)
        assert_pico_ok(self.status["setChA"])

        # Set up channel B
        chBRange = 8
        self.status["setChB"] = ps.ps4000aSetChannel(self.chandle, 1, 1, 1, chBRange, 0)
        assert_pico_ok(self.status["setChB"])

        # Set up channel C
        chCRange = 8
        self.status["setChC"] = ps.ps4000aSetChannel(self.chandle, 2, 1, 1, chCRange, 0)
        assert_pico_ok(self.status["setChC"])

        # Set up channel D
        chDRange = 8
        self.status["setChD"] = ps.ps4000aSetChannel(self.chandle, 3, 1, 1, chDRange, 0)
        assert_pico_ok(self.status["setChD"])

        # Set up channel E
        chERange = 7
        self.status["setChE"] = ps.ps4000aSetChannel(self.chandle, 4, 0, 1, chERange, 0)
        assert_pico_ok(self.status["setChE"])

        # Set up channel F
        chFRange = 7
        self.status["setChF"] = ps.ps4000aSetChannel(self.chandle, 5, 0, 1, chFRange, 0)
        assert_pico_ok(self.status["setChF"])

        # Set up channel G
        chGRange = 7
        self.status["setChG"] = ps.ps4000aSetChannel(self.chandle, 6, 0, 1, chGRange, 0)
        assert_pico_ok(self.status["setChG"])

        # Set up channel H
        chHRange = 7
        self.status["setChH"] = ps.ps4000aSetChannel(self.chandle, 7, 0, 1, chHRange, 0)
        assert_pico_ok(self.status["setChH"])

    # Set up single trigger
    # handle = chandle
    # enabled = 1
    # source = PS4000a_CHANNEL_A = 0
    # threshold = 1024 ADC counts
    # direction = PS4000a_RISING = 2
    # delay = 0 s
    # auto Trigger = 1000 ms
    def set_trigger(self):
        self.status["trigger"] = ps.ps4000aSetSimpleTrigger(self.chandle, 1, 1, 8200, 2, 0,
                                                       00)  # This sets a trigger level of 1.25V. This WILL negelect -1.25 V. Needs optimization
        assert_pico_ok(self.status["trigger"])

    # Get timebase information
    # handle = chandle
    # timebase = 8 = timebase
    # noSamples = maxSamples
    # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
    # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
    # segment index = 0
    def set_timebase(self):
        timebase = 64  # Sample period of 1.24 uS
        timeIntervalns = ctypes.c_float()
        returnedMaxSamples = ctypes.c_int32()
        oversample = ctypes.c_int16(1)
        self.status["getTimebase2"] = ps.ps4000aGetTimebase2(self.chandle, timebase, self.maxSamples, ctypes.byref(timeIntervalns),
                                                        ctypes.byref(returnedMaxSamples), 0)
        assert_pico_ok(self.status["getTimebase2"])

    # Run block capture
    # handle = chandle
    # number of pre-trigger samples = preTriggerSamples
    # number of post-trigger samples = PostTriggerSamples
    # timebase = 3 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
    # time indisposed ms = None (not needed in the example)
    # segment index = 0
    # lpReady = None (using ps4000aIsReady rather than ps4000aBlockReady)
    # pParameter = None
    def run_block_capture(self):
        self.status["runBlock"] = ps.ps4000aRunBlock(self.chandle, self.preTriggerSamples, self.postTriggerSamples, self.timebase, None, 0, None,
                                                None)
        assert_pico_ok(self.status["runBlock"])

    # Check for data collection to finish using ps4000aIsReady
    def ready(self):
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = ps.ps4000aIsReady(self.chandle, ctypes.byref(ready))

    # Set data buffer location for data collection from channel A
    # handle = chandle
    # source = PS4000a_CHANNEL_A = 0, ..., PS4000a_CHANNEL_D = 3
    # pointer to buffer max
    # pointer to buffer min
    # buffer length = maxSamples
    # segementIndex = 0
    # mode = PS4000A_RATIO_MODE_NONE = 0
    def set_buffer_location(self):
        self.status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(self.chandle, 0, ctypes.byref(self.bufferAMax),
                                                             ctypes.byref(self.bufferAMin), self.maxSamples, 0, 0)
        assert_pico_ok(self.status["setDataBuffersA"])

        self.status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(self.chandle, 1, ctypes.byref(self.bufferBMax),
                                                             ctypes.byref(self.bufferBMin), self.maxSamples, 0, 0)
        assert_pico_ok(self.status["setDataBuffersB"])

        self.status["setDataBuffersC"] = ps.ps4000aSetDataBuffers(self.chandle, 2, ctypes.byref(self.bufferCMax),
                                                             ctypes.byref(self.bufferCMin), self.maxSamples, 0, 0)
        assert_pico_ok(self.status["setDataBuffersC"])

        self.status["setDataBuffersD"] = ps.ps4000aSetDataBuffers(self.chandle, 3, ctypes.byref(self.bufferDMax),
                                                             ctypes.byref(self.bufferDMin), self.maxSamples, 0, 0)
        assert_pico_ok(self.status["setDataBuffersD"])

    # Retrieved data from scope to buffers assigned above
    # handle = chandle
    # start index = 0
    # pointer to number of samples = ctypes.byref(cmaxSamples)
    # downsample ratio = 0
    # downsample ratio mode = PS4000a_RATIO_MODE_NONE
    # pointer to overflow = ctypes.byref(overflow))
    def getData(self):
        self.status["getValues"] = ps.ps4000aGetValues(self.chandle, 0, ctypes.byref(self.cmaxSamples), 0, 0, 0,
                                                  ctypes.byref(self.overflow))
        assert_pico_ok(self.status["getValues"])

        # find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        maxADC = ctypes.c_int16(32767)

        # convert ADC counts data to mV
        adc2mVChAMax = adc2mV(self.bufferAMax, self.chARange, maxADC)
        adc2mVChBMax = adc2mV(self.bufferBMax, self.chBRange, maxADC)
        adc2mVChCMax = adc2mV(self.bufferCMax, self.chCRange, maxADC)
        adc2mVChDMax = adc2mV(self.bufferDMax, self.chDRange, maxADC)
        # Create time data
        time = np.linspace(0, self.cmaxSamples.value * self.timeIntervalns.value, self.cmaxSamples.value)
        return np.stack(time, adc2mVChAMax, adc2mVChBMax, adc2mVChCMax, adc2mVChDMax)

    # detect the ping in the numpy array that the ping is at and return the start and end indexes
    def detect_ping(self, ch, time):
        index = 0
        while index < len(ch):
            if abs(ch[index]) > self.ping_detect:
                start = index
                end = self.end_ping(self, ch, index)
                return start, end
            index += 1
        return -1, -1

    # find the end index of the ping in the array
    def end_ping(self, ch, index):
        noise_counter = 0
        while noise_counter < self.noise_length and index < len(ch):
            if abs(ch[index]) > self.ping_detect:
                noise_counter = 0
            index += 1
            noise_counter += 1
        return index

import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import csv
import Acoustics


def main():
    a = Acoustics
    data = a.get_data()
    channel_a = a.detectPing(data[0], data[1])
    channel_b = a.detectPing(data[0], data[2])
    channel_c = a.detectPing(data[0], data[3])
    channel_d = a.detectPing(data[0], data[4])

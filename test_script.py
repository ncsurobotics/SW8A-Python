#!/bin/python3

import readline
import sys
sys.path.append('object_orientation/')
from pico_4000a import Pico_4000a
from pico_2000a import Pico_2000a

try:
    num_channels = int(input("Number of channels: "))
# Default of 4 channels
except ValueError:
    num_channels = 4
run = 1

scope = Pico_4000a(num_channels)
while True:
    try:
        trigger_channel = int(input("Trigger channel: "))
    except ValueError:
        trigger_channel = 0
    try:
        trigger_frequency = float(input("Trigger frequency (Hz): "))
    except ValueError:
        trigger_frequency = 9.98e7
    try:
        trigger_threshold = float(input("Trigger threshold (Volts): "))
    except ValueError:
        trigger_threshold = 0.5
    try:
        auto_trigger = int(input("Auto Trigger: "))
    except ValueError:
        auto_trigger = 0

    print("Initializing...")
    scope.initialize(trigger_channel, trigger_frequency, trigger_threshold, auto_trigger)
    while True:
        name = input("Run name: ")
        # Number from 1, when no name is provided
        if name == '':
            name = run
            run += 1
            print("Run #" + str(name))
        print("Running...")
        scope.run(name)
        scope.write_csv()
        print("Plotting...")
        scope.write_plot()
        scope.show_plot()
        run_again = input("Run again? (Y/n): ")
        if run_again in ("n","N"):
            break
    scope.close()
    change_params = input("Change initialization parameters? (Y/n): ")
    if change_params in ("n","N"):
        break

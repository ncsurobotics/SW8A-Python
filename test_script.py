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

try:
    model = int(input("Model (4 or 2): "))
    if model == 2:
        scope = Pico_2000a(num_channels)
    else:
        scope = Pico_4000a(num_channels)
except ValueError:
    scope = Pico_2000a(num_channels)

while True:
    try:
        trigger_channel = int(input("Trigger channel: "))
    except ValueError:
        trigger_channel = 0
    try:
        sample_length = float(input("Sample Length (s): "))
    except ValueError:
        sample_length = 5e-3
    try:
        trigger_threshold = float(input("Trigger threshold (Volts): "))
    except ValueError:
        trigger_threshold = 0.5
    try:
        auto_trigger = int(input("Auto Trigger: "))
    except ValueError:
        auto_trigger = 0

    print("Initializing...")
    scope.initialize(trigger_channel, sample_length, trigger_threshold, auto_trigger)
    while True:
        try:
            batch_size = int(input("Batch num: "))
        except ValueError:
            batch_size = 1
        name = input("Run name: ")
        # Number from 1, when no name is provided
        if name == '':
            name = str(run)
            run += 1
            print("Run #" + name)
        count = 0
        while count < int(batch_size):
            batch_name = name + "_" + str(count)
            print("Batch Run: " + batch_name)
            print("Running...")
            scope.run(batch_name)
            scope.write_csv()
            print("Plotting...")
            scope.write_plot()
            scope.show_plot()
            count = count + 1
        run_again = input("Run again? (Y/n): ")
        if run_again in ("n","N"):
            break
    scope.close()
    change_params = input("Change initialization parameters? (Y/n): ")
    if change_params in ("n","N"):
        break

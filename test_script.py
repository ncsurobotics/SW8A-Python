import sys
sys.path.append('object_orientation/')
from pico_4000a import Pico_4000a
from pico_2000a import Pico_2000a

try:
    num_channels = int(raw_input("Number of channels: "))
# Default of 4 channels
except ValueError:
    num_channels = 4
run = 1

scope = pico_4000a(num_channels)
while True:
    try:
        trigger_channel = int(raw_input("Trigger channel: "))
    except ValueError:
        trigger_channel = 0
    try:
        trigger_frequency = float(raw_input("Trigger frequency (Hz): "))
    except ValueError:
        trigger_frequency = 9.98e7
    try:
        trigger_threshold = float(raw_input("Trigger threshold (Volts): "))
    except ValueError:
        trigger_threshold = 0.5
    try:
        auto_trigger = int(raw_input("Auto Trigger: "))
    except ValueError:
        auto_trigger = 0

    scope.initialize(trigger_channel, trigger_frequency, trigger_threshold, auto_trigger)
    while True:
        name = raw_input("Run name: ")
        # Number from 1, when no name is provided
        if name == '':
            name = run
            run += 1
            print("Run #" + str(name))
        print("Initializing...")
        print("Running...")
        scope.run()
        scope.write_csv()
        print("Plotting...")
        scope.write_plot()
        scope.show_plot()
        a.stop()
        run_again = raw_input("Run again? (Y/n): ")
        if run_again in ("n","N"):
            break
    change_params = raw_input("Change initialization paramters? (Y/n): ")
    if change_params in ("n","N"):
        scope.end()
        break

import sys
sys.path.append('object_orientation/')
from acousticsObjOri import Acoustics

try:
    num_channels = int(raw_input("Number of channels: "))
# Default of 4 channels
except ValueError:
    num_channels = 4
run = 1
while True:
    name = raw_input("Run name: ")
    # Number from 1, when no name is provided
    if name == '':
        name = run
        run += 1
        print("Run #" + str(name))
    a = Acoustics(name, num_channels, 0, 0)
    print("Initializing...")
    a.initialize()
    print("Running...")
    a.run()
    a.write_csv()
    print("Plotting...")
    a.write_plot()
    a.show_plot()
    print("Plotted.")
    a.stop()
    run_again = raw_input("Run again? (Y/n): ")
    if run_again in ("n","N"):
        break

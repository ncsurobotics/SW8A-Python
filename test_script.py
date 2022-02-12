import sys
sys.path.append('object_orientation/')
from acousticsObjOri import Acoustics

num_channels = input("Number of channels: ")
if num_channels == '':
    num_channels = 4
run = 0
while True:
    a = Acoustics(run, num_channels, 0, 0)
    a.initialize()
    a.run()
    a.write_csv()
    a.write_plot()
    a.show_plot()
    a.stop()
    run_again = input("Run again? (Y/n): ")
    if run_again in ("n","N"):
        break
    run += 1

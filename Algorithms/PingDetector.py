import numpy as np
import matplotlib.pyplot as plt

ping_detect = 0.025
noise_length = 100

index = 0
output_text = ""


def end_ping(time, ch):
    global index
    global output_text
    end = 0
    noise_counter = 0
    while noise_counter < noise_length and index < len(ch):
        if abs(ch[index]) > ping_detect:
            end = time[index]
            noise_counter = 0
        index += 1
        noise_counter += 1
    return end, index


def get_ping(ch):
    global index
    global output_text
    while index < len(ch):
        if abs(ch[index]) > ping_detect:
            start = (t[index], index)
            temp = "Start: " + str(start) + "\n"
            output_text += temp
            temp = "End: " + str(end_ping(t, ch)) + "\n"
            output_text += temp
        index += 1


file_in_name = input("Enter input file name: ")

data = []
data = np.genfromtxt(file_in_name, delimiter=",", skip_header = 1)

t = data[0]
ch1 = data[1]
ch2 = data[2]
ch3 = data[3]
ch4 = data[4]

title = "Channel 1\n"
output_text += title
get_ping(ch1)

index = 0
title = "\nChannel 2\n"
output_text += title
get_ping(ch2)

index = 0
title = "\nChannel 3\n"
output_text += title
get_ping(ch3)

index = 0
title = "\nChannel 4"
output_text += title
get_ping(ch4)

print(output_text)

file_out_name = input("Enter output file name: ")
file_out = open(file_out_name, "w")
file_out.write(output_text)
file_out.close()

fig, axs = plt.subplots(2, 2)

axs[0, 0].plot(t, ch1)
axs[0, 0].set_title('Channel 1')
axs[0, 1].plot(t, ch2, 'tab:orange')
axs[0, 1].set_title('Channel 2')
axs[1, 0].plot(t, ch3, 'tab:green')
axs[1, 0].set_title('Channel 3')
axs[1, 1].plot(t, ch4, 'tab:red')
axs[1, 1].set_title('Channel 4')

for ax in axs.flat:
    ax.set(xlabel='Time (ms)', ylabel='Signal (V)')

fig.tight_layout()
plt.show()

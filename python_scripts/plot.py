import sys
from read_csv import read_and_filter
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    file_num = len(sys.argv) - 1
    csi_list = []
    filterd_csi_list = []
    for i in range(1, file_num+1):
        amp, filterd_amp = read_and_filter(sys.argv[i])
        csi_list.append(amp)
        filterd_csi_list.append(filterd_amp)

    fig, axs = plt.subplots(2*file_num)
    fig.suptitle('LLTF AMP')

    for i in range(0, file_num):
        for subc_index in range(2, 28):
            x = np.arange(len(filterd_csi_list[i][2]))
            axs[i*2].plot(x, csi_list[i][subc_index])
            axs[i*2+1].plot(x, filterd_csi_list[i][subc_index])
            axs[i*2+1].set_title(sys.argv[i+1][27:])
    plt.show()

    
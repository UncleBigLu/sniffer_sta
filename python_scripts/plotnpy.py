import sys
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    filename = str(sys.argv[1])
    filterd_amp = np.load(filename)

    fig, axs = plt.subplots()
    fig.suptitle('LLTF AMP')
    x = np.arange(len(filterd_amp[2]))
    for subc_index in range(2, 28):
        axs.plot(x, filterd_amp[subc_index])

    plt.show()
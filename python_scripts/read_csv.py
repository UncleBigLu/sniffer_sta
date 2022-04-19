from math import sqrt
from math import atan2
import matplotlib.pyplot as plt
import numpy
import numpy as np
from scipy.ndimage import gaussian_filter
import sys
from myLOF import lof
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean



def hampel_filter(subc, window_size = 25):
    i = 0
    while(i < len(subc) - window_size + 1):
        mdn = np.median(subc[i:i+window_size])
        mad_arr = np.copy(subc[i:i+window_size])
        for j in range(0, len(mad_arr)):
            mad_arr[j] = abs(mad_arr[j]-mdn)
        mad = np.median(mad_arr)
        for k in range(i, i+window_size):
            if(abs(subc[k] - mdn) > 3*1.4826*mad):
                subc[k] = mdn
        i += window_size
    if i < len(subc):
        for k in range(i, len(subc)):
            if(abs(subc[k] - mdn > 3*1.4826*mad)):
                subc[k] = mdn

def read_csv_alldata(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        csi_num = len(lines)
        # Count data length
        d = {}
        for line in lines:
            l = line.strip('\n')
            l = l.strip('csi_data: ')
            csi_str = l.split(' ')
            subc_num = len(csi_str)
            if(subc_num not in d):
                d[subc_num] = 1
            else:
                d[subc_num] += 1
        print(d)
        print(csi_num)

def read_csv(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        csi_num = len(lines)
        # 64 subcarriers * csi_num array
        subc_amplitude = np.zeros((64, csi_num))
        subc_phase = np.zeros((64, csi_num))
        valid_csi_num = 0
        for line in lines:
            l = line.strip('\n')
            l = l.strip('csi_data: ')
            csi_str = l.split(' ')
            # 64 subcarriers of lltf
            i = 0
            while (i < 128):
                amp = sqrt(int(csi_str[i]) ** 2 + int(csi_str[i + 1]) ** 2)
                # atan2(img, real)
                pha = atan2(int(csi_str[i]), int(csi_str[i + 1]))
                subc_amplitude[int(i / 2)][valid_csi_num] = amp
                subc_phase[int(i / 2)][valid_csi_num] = pha
                i = i + 2
            valid_csi_num = valid_csi_num + 1
    return subc_amplitude, subc_phase


def read_and_filter(filename, gaussian_sigma=5):
    subc_amplitude, subc_phase = read_csv(filename)
    csi_num = len(subc_amplitude[0])
    # remove_outlier(subc_amplitude)
    for subc_index in range(0, 64):
        hampel_filter(subc_amplitude[subc_index])

    # Apply gaussian filter
    filterd_amplitude = np.empty((64, csi_num))
    for i in range(0, 64):
        filterd_amplitude[i] = gaussian_filter(subc_amplitude[i], sigma=gaussian_sigma)
    return subc_amplitude, filterd_amplitude


if __name__ == '__main__':
    filename = str(sys.argv[1])
    subc_amplitude, subc_phase = read_csv(filename)
    csi_num = len(subc_amplitude[0])
    # remove_outlier(subc_amplitude)
    for subc_index in range(0, 64):
        hampel_filter(subc_amplitude[subc_index])
    amp_list = []
    for sigma in range(13, 19):
        filterd_amplitude = np.empty((64, csi_num))
        for i in range(0, 64):
            filterd_amplitude[i] = gaussian_filter(subc_amplitude[i], sigma=sigma)
        amp_list.append(filterd_amplitude)
    fig, ax = plt.subplots(3, 2)
    for i in range(0, 6):
        x = np.arange(len(amp_list[i][2]))
        print(i)
        ax[int(i / 2)][i % 2].set_title('sigma: '+ str(i+13))
        for subc_index in range(2, 28):
            ax[int(i/2)][i%2].plot(x, amp_list[i][subc_index])
    plt.show()



import numpy as np


def subc_amp_std(subc_amp, window_size=50):
    l = len(subc_amp)
    std_arr = np.zeros(l)
    for i in range(0, l - window_size + 1):
        amp_window = subc_amp[i:i + window_size]
        std_arr[i] = np.std(amp_window)
    std_arr[l - window_size:l] = std_arr[l - window_size]
    return std_arr

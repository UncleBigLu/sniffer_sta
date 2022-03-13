import sys
from read_csv import read_and_filter
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean


if __name__ == '__main__':
    csi_list = []
    filterd_csi_list = []
    for f in sys.argv[1:]:
        amp, filterd_amp = read_and_filter(f)
        csi_list.append(amp)
        filterd_csi_list.append(filterd_amp)

    # Calculate dynamic time warping
    distance_list = []
    for i in range(2, 22, 5):
        distance, path = fastdtw(filterd_csi_list[0][i][300:1000], filterd_csi_list[1][i][300:1000], dist=euclidean)
        distance_list.append(distance/len(path))

    print(distance_list)

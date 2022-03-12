from math import sqrt
from math import atan2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
import sys
from myLOF import lof
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean


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

def remove_outlier(subc, threshold=20):
    csi_num = len(subc[2])
    for subc_index in range(2, 28):
        k_dis_arr = lof(subc[subc_index])
        for i in range(0, csi_num):
            if(k_dis_arr[i] > threshold):
                j = i
                k = i
                while(k_dis_arr[j] > threshold and k_dis_arr[k] > threshold):
                    if(j != 0):
                        j -= 1
                    if(k != csi_num-1):
                        k += 1
                    if(j == 0 and k == csi_num - 1):
                        break
                if(k_dis_arr[j] <= threshold):
                    subc[subc_index][i] = subc[subc_index][j]
                elif(k_dis_arr[k] <= threshold):
                    subc[subc_index][i] = subc[subc_index][j]
                else:
                    print("K Neighbor error at i:"+str(i))

def read_and_filter(filename):
    subc_amplitude, subc_phase = read_csv(filename)
    csi_num = len(subc_amplitude[0])
    remove_outlier(subc_amplitude)
    # Apply gaussian filter
    filterd_amplitude = np.empty((64, csi_num))
    for i in range(0, 64):
        filterd_amplitude[i] = gaussian_filter(subc_amplitude[i], sigma=5)
    return subc_amplitude, filterd_amplitude

if __name__ == '__main__':

    subc_list = []
    for i in range(1, 3):
        subc_amplitude, filterd_amplitude = read_and_filter(sys.argv[i])
        subc_list.append(subc_amplitude)
        subc_list.append(filterd_amplitude)



    # Calculate amplitude standard deviation
    # filterd_std = np.empty((64, csi_num))
    # subc_std = np.empty((64, csi_num))
    # for i in range(0, 64):
    #     filterd_std[i] = myMath.subc_amp_std(filterd_amplitude[i])
    #     subc_std[i] = myMath.subc_amp_std(subc_amplitude[i])

    # Plot LLTF CSI
    fig, axs = plt.subplots(3)
    fig.suptitle('LLTF subcarrier CSI amp and dwt')

    # Dynamic time warping
    distance_list = []
    path_list = []
    # for i in range(2, 7):
    #     distance, path = fastdtw(subc_list[1][i], subc_list[3][i], dist=euclidean)
    #     distance_list.append(distance)
    #     path_list.append(path)
    # print(distance_list)
    subc_idle1 = subc_list[1][:, 0:350]
    subc_idle2 = subc_list[3][:, 0:500]
    subc_walk1 = subc_list[1][:, 400:]
    subc_walk2 = subc_list[3][:, 550:]

    for i in range(2, 7):
        #distance, path = fastdtw(subc_walk1[i], subc_walk2[i], dist=euclidean)
        distance, path = fastdtw(subc_idle1[i], subc_walk2[i], dist=euclidean)
        distance_list.append(distance)
        path_list.append(path)
    print(distance_list)


    x = np.arange(len(subc_idle1[2]))
    y = np.arange(len(subc_idle2[2]))
    j = np.arange(len(subc_walk1[2]))
    k = np.arange(len(subc_walk2[2]))

    for i in range(2, 7):
        axs[0].plot(j, subc_walk1[i])
        axs[1].plot(k, subc_walk2[i])
        # axs[2].plot(y, dtw_arr[i-2])

    plt.show()

    # dtw_arr = np.zeros((5, len(subc_list[3][2])))
    # print(dtw_arr.shape)
    # for i in range(0, 5):
    #     avergae = 0
    #     cnt = 0
    #     for j in range(0, len(path_list[i])-1):
    #         avergae += subc_list[1][i][path_list[i][j][0]]
    #         cnt += 1
    #         if (path_list[i][j][1] != path_list[i][j + 1][1]):
    #
    #             dtw_arr[i][path_list[i][j][1]] = avergae/cnt
    #             avergae = 0
    #             cnt = 0
    #     if(avergae != 0):
    #         avergae += subc_list[1][i][-1]
    #         dtw_arr[i][-1] = avergae/(cnt+1)
    #         avergae = 0
    #         cnt = 0
    #     else:
    #         dtw_arr[i][-1] = subc_list[1][i][-1]


    #
    # x = np.arange(len(subc_list[1][2]))
    # y = np.arange(len(subc_list[3][2]))
    #
    # for i in range(2, 7):
    #     axs[0].plot(x, subc_list[1][i])
    #     axs[1].plot(y, subc_list[3][i])
    #     # axs[2].plot(y, dtw_arr[i-2])
    #
    # plt.show()



    # # base_amp = filterd_amplitude[2:28].T
    # # cov_amp = np.cov(base_amp)[50]
    # # print(cov_amp)
    # # x = np.arange(csi_num)
    # # axs[0].plot(x, cov_amp)
    # # plt.show()
    # x = np.arange(csi_num)
    # for i in range(2, 28):
    #     # axs[0].plot(x, subc_amplitude[i])
    #     axs[0].plot(x, subc_amplitude[i])
    #     # axs[1].plot(x, filterd_amplitude[i])
    #     axs[1].plot(x, filterd_amplitude[i])
    # for i in range(29, 55):
    #     axs[1].plot(x, filterd_amplitude[i], label="subcarrier " + str(i))
    # for i in range(62, 64):
    #     axs[2].plot(x, filterd_amplitude[i], label="subcarrier " + str(i))

    # # Calculate covariance between subcarriers
    # # In this test we calculate cov of lltf subcarriers 2~20
    # amp_cov = np.zeros(18)
    # amp_avg = np.zeros(18)
    #
    # for i in range(2, 20):
    #     amp_avg[i - 2] = sum(filterd_amplitude[i]) / csi_num
    # for i in range(0, 17):
    #     for j in range(0, csi_num):
    #         amp_cov[i] += (filterd_amplitude[i+2][j] - amp_avg[i])*(filterd_amplitude[i+3][j] - amp_avg[i+1])/csi_num
    # for j in range(0, csi_num):
    #     amp_cov[17] += (filterd_amplitude[19][j] - amp_avg[17])*(filterd_amplitude[2][j] - amp_avg[0])/csi_num
    #
    # print(amp_cov)

    # axs[0].legend()
    # plt.show()

    # for i in range(0, 64):
    #     x = [j for j in range(0, len(subc_amplitude[i]))]
    #     plt.plot(x, subc_phase[i], label="subc"+str(i))
    # plt.legend()
    # plt.show()









import sys
from read_csv import read_and_filter
import matplotlib.pyplot as plt
import numpy as np
import pywt
from math import ceil


def plot_all_subc(subcs, start_subc=0, end_subc=64):
    subc_num = end_subc - start_subc
    fig, axs = plt.subplots(8, ceil(subc_num/8) )
    x = np.arange(len(subcs[0]))

    cnt = 0
    for subc_index in range(start_subc, end_subc):
        axs[int(cnt/8), cnt%8].plot(x, subcs[subc_index])
        axs[int(cnt/8), cnt%8].set_title('Subcarrier '+ str(subc_index))
        cnt += 1
    plt.show()


def plot_subc_one_ax(subcs, start_subc=2, end_subc=55):
    fig, axs = plt.subplots()
    x = np.arange(len(subcs[start_subc]))
    for i in range(start_subc, end_subc):
        print(i)
        axs.plot(x, subcs[i])
    plt.show()


def calc_subc_distance(subcs, interval=1, start_subc=2, end_subc=55):
    subc_num = end_subc - start_subc
    data_num = len(subcs[start_subc])
    subc_distance_list = []

    subcs_zero_center = []
    # Zero-center all subcarrier to calculate their distance
    for i in range(start_subc, end_subc):
        subcs_zero_center.append(subcs[i]-np.average(subcs[i]))
    # Plot all subcarrier to check if data is correct
    # plot_subc_one_ax(subcs_zero_center, 0, end_subc-start_subc)
    for i in range(0, end_subc-interval-start_subc):
        # Calculate subcarrier similarity
        distance = np.abs(subcs_zero_center[i+interval]-subcs_zero_center[i])
        subc_distance_list.append(np.average(distance))
    return np.average(subc_distance_list)


if __name__ == '__main__':
    file_num = len(sys.argv) - 1
    csi_list = []
    filterd_csi_list = []
    for i in range(1, file_num+1):
        amp, filterd_amp = read_and_filter(sys.argv[i])
        csi_list.append(amp)
        filterd_csi_list.append(filterd_amp)

    # fig, axs = plt.subplots(2*file_num)
    # fig.suptitle('LLTF AMP')

    for i in range(0, file_num):
    #     for subc_index in range(2, 3):
    #         x = np.arange(len(csi_list[i][2]))
    #         # Discrete wavelet transform
    #         cA, cD = pywt.dwt(csi_list[i][subc_index], 'db2')
    #         # cA2,cD2 = pywt.dwt(cA, 'db2')
    #         # cA3,cD3 = pywt.dwt(cA2, 'db2')
    #         # cA4,cD4 = pywt.dwt(cA3, 'db2')
    #         # print(cA)
    #         print("cA: "+str(len(cA)))
    #         print("cD: "+ str(len(cD)))
    #         print("csi_len: "+str(len(csi_list[i][subc_index])))
    #         y = np.arange(len(cA))
    #
    #         axs[i * 2].plot(x, csi_list[i][subc_index])
    #         # axs[i*2].plot(x, csi_list[i][subc_index])
    #         # axs[i * 2].plot(y, cD)
    #         # axs[i*2+1].plot(x, filterd_csi_list[i][subc_index])
    #         axs[i * 2 + 1].plot(y, cA)
    #
    #         axs[i*2+1].set_title(sys.argv[i+1][27:])
    # plt.show()
        similarity_list = []
        for subc_itv in range(1, 40):
            similarity_list.append(calc_subc_distance(filterd_csi_list[i], subc_itv))
        x = np.arange(1, 40)
        fig, ax = plt.subplots()
        ax.set_xlabel('subcarrier interval')
        ax.set_ylabel('subcarrier distance')
        ax.plot(x, similarity_list)
        fig.suptitle('subcarrier_similarity')
        plt.show()
    
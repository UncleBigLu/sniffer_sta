#!/usr/bin/env python3


import sys

import numpy

from read_csv import read_and_filter, read_csv_all_data
import matplotlib.pyplot as plt
import numpy as np
import pywt
from math import ceil
from scipy.stats import median_abs_deviation
from scipy.spatial.distance import euclidean
import argparse
from fastdtw import fastdtw


def plot_all_subc(subcs, start_subc=0, end_subc=64):
    subc_num = end_subc - start_subc
    fig, axs = plt.subplots(8, ceil(subc_num / 8))
    x = np.arange(len(subcs[0]))

    cnt = 0
    for subc_index in range(start_subc, end_subc):
        axs[int(cnt % 8), int(cnt / 8)].plot(x, subcs[subc_index])
        axs[int(cnt % 8), int(cnt / 8)].set_title('Subcarrier ' + str(subc_index + 2))
        cnt += 1
    plt.show()


def plot_subc_one_ax(subcs, start_subc=2, end_subc=55):
    fig, axs = plt.subplots()
    x = np.arange(len(subcs[start_subc]))
    for i in range(start_subc, end_subc):
        axs.plot(x, subcs[i])
    plt.show()


def calc_subc_distance(subcs, interval=1, start_subc=2, end_subc=55):
    subc_num = end_subc - start_subc
    data_num = len(subcs[start_subc])
    subc_distance_list = []

    subcs_zero_center = []
    # Zero-center all subcarrier to calculate their distance
    for i in range(start_subc, end_subc):
        subcs_zero_center.append(subcs[i] - np.average(subcs[i]))
    # Plot all subcarrier to check if data is correct
    # plot_subc_one_ax(subcs_zero_center, 0, end_subc-start_subc)
    for i in range(0, end_subc - interval - start_subc):
        # Calculate subcarrier similarity
        distance = np.abs(subcs_zero_center[i + interval] - subcs_zero_center[i])
        subc_distance_list.append(np.average(distance))
    return np.average(subc_distance_list)


def plot_subc_distance(filename):
    amp, filterd_amp = read_and_filter(filename)
    dis_list = []
    for interval in range(1, 40):
        dis_list.append(calc_subc_distance(filterd_amp, interval))
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots()
    x = np.arange(len(dis_list)) + 1
    ax.plot(x, dis_list)

    ax.set_xlabel('subcarrier interval', fontsize=22)
    ax.set_ylabel('subcarrier distance', fontsize=22)
    ax.set(xticks=np.arange(0, 40, 5))
    ax.tick_params(axis='both', which='major', labelsize=22)
    ax.tick_params(axis='both', which='minor', labelsize=22)

    plt.show()


def calc_subc_variance(subcs, start_datapoint, end_datapoint, start_subc=2, end_subc=55):
    variance_list = []
    for i in range(start_subc, end_subc):
        variance_list.append(np.var(subcs[i][start_datapoint:end_datapoint]))
    return variance_list


def sort_subc_sensitivity(var_list_idle, var_list_move, start_subc=2, end_subc=55):
    # weight_move*var_move + weight_idle*(1-var_idle)
    weight_move = 0.5
    weight_idle = 1 - weight_move
    weight_list = []
    for i in range(start_subc, end_subc):
        weight_list.append(
            weight_move * var_list_move[i - start_subc] + weight_idle * (1 - var_list_idle[i - start_subc]))
    return weight_list


def plot_subc_sensitivity(weight_list, start_subc=2, end_subc=62):
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots()
    x = np.arange(len(weight_list)) + start_subc + 2
    ax.bar(x, weight_list, width=1, edgecolor='white', linewidth=0.7)
    # ax.set(xlim=(start_subc, end_subc), xticks=np.arange(start_subc, end_subc))

    plt.show()


def plot_spec_subc(filename, start_datapoint, end_datapoint, raw_data, hampel_only, *subc_seq):
    if raw_data:
        amp = read_csv_all_data(filename)
    else:
        raw_amp, filtered_amp = read_and_filter(filename)
        if hampel_only:
            amp = raw_amp
        else:
            amp = filtered_amp
    subc_num = len(subc_seq)
    if subc_num == 0:
        print("No subcarrier number given")
        return



    # plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots(subc_num, figsize=(6.93, 5.19))
    # ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, labelleft=False,
    #                labelbottom=False)
    x = np.arange(end_datapoint - start_datapoint)
    if subc_num == 1:
        ax.plot(x, amp[int(subc_seq[0]) - 4][int(start_datapoint):int(end_datapoint)], label='amp')
        ax.set_title('subcarrier' + str(subc_seq[0]))
        ax.set_xlabel('index', fontsize=22)
        ax.set_ylabel('subcarrier amplitude', fontsize=22)
    else:
        for i in range(0, subc_num):
            ax[i].plot(x, amp[int(subc_seq[i]) - 4][int(start_datapoint):int(end_datapoint)], label='amp')
            ax[i].set_title('subcarrier' + str(subc_seq[i]))
            ax[i].set_xlabel('subcarrier interval', fontsize=22)
            ax[i].set_ylabel('subcarrier distance', fontsize=22)
    # ax.legend()
    plt.show()
    fig.savefig('test.png', format='png')

    s = ''
    if subc_num == 1:
        for v in amp[int(subc_seq[0]) - 4][int(start_datapoint):int(end_datapoint)]:
            s += str(v)
            s += ' '
    else:
        for i in range(0, subc_num):
            for v in amp[int(subc_seq[i]) - 4][int(start_datapoint):int(end_datapoint)]:
                s += str(v)
                s += ' '
            s += '\n'
    print(s)
    return amp[int(subc_seq[0]) - 4][int(start_datapoint):int(end_datapoint)]


def init_plot():
    fig, ax = fig, ax = plt.subplots(figsize=(6.93, 5.19))
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, labelleft=False, labelbottom=False)
    return fig, ax


def plot_val(fig, ax, val, label=None):
    x = np.arange(len(val))
    ax.plot(x, val, label=label)



def discrete_wavelet_transform(filename, base='db1', level=4, gaussian_sigma=5, result_only=False):
    amp, subcs = read_and_filter(filename, gaussian_sigma)
    subc_seq_index = 118 - 4
    coeffs = pywt.wavedec(subcs[subc_seq_index], base, level=level)
    plt.style.use('_mpl-gallery')
    if not result_only:
        fig, axs = plt.subplots(level + 3)
    else:
        fig, axs = plt.subplots(3)
    axs[0].plot(np.arange(len(subcs[subc_seq_index])), subcs[subc_seq_index])
    axs[0].set_xlabel('index', fontsize=20)
    axs[0].set_ylabel('value', fontsize=20)
    axs[0].set_title('origin data', fontsize=22)

    i = 1
    coeffs_backup = coeffs
    if result_only:
        coeffs = [coeffs[0]]
    for e in reversed(coeffs):
        axs[i].plot(np.arange(len(e)), e)
        axs[i].set_xlabel('index', fontsize=20)
        axs[i].set_ylabel('value', fontsize=20)
        if i <= len(coeffs) - 1:
            axs[i].set_title('detail coefficients ' + str(i), fontsize=22)
        else:
            axs[i].set_title('approximation coefficients', fontsize=22)
        i += 1
    # Inverse DWT
    # coeffs_backup[-1] = np.zeros_like(coeffs[-1])
    # coeffs_backup[-2] = np.zeros_like(coeffs[-2])
    # coeffs_backup[-3] = np.zeros_like(coeffs[-3])
    # idwt_amp = pywt.waverec(coeffs_backup, base)
    # idwt_amp = pywt.upcoef('a', coeffs[0], base)
    # axs[-1].plot(np.arange(len(idwt_amp)), idwt_amp)
    plt.show()
    return subcs[subc_seq_index], coeffs[0]


def main_backup():
    file_num = len(sys.argv) - 1
    csi_list = []
    filterd_csi_list = []
    for i in range(1, file_num + 1):
        amp, filterd_amp = read_and_filter(sys.argv[i])
        csi_list.append(amp)
        filterd_csi_list.append(filterd_amp)

    # fig, axs = plt.subplots(2*file_num)
    # fig.suptitle('LLTF AMP')
    weight_avg = []
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
        plot_spec_subc(filterd_csi_list[i], 0, 1000, 45, 57, 118, 98)


def plot_line(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        fig, axs = plt.subplots()
        i = 0
        for line in lines:
            amp = line.split()
            np_amp = np.empty(len(amp))
            for j in range(0, len(amp)):
                np_amp[j] = float(amp[j])
            x = np.arange(len(amp))
            axs.plot(x, np_amp)
            i += 1
        plt.show()


def plot_amp():
    filename = sys.argv[1]
    fig, axs = plt.subplots(4)
    csi_lists = []
    # Read data to lists
    with open(filename, 'r') as f:
        for i in range(0, 4):
            line = f.readline()
            line = line.strip('\n')
            csi_str_list = line.split()
            csi_lists.append(csi_str_list)
    tags = ['45', '57', '98', '118']
    csi_arr = numpy.empty((4, len(csi_lists[0])))
    # Put data to numpy arr
    for subc_index in range(0, 4):
        for data_index in range(len(csi_lists[subc_index])):
            csi_arr[subc_index][data_index] = float(csi_lists[subc_index][data_index])
    # Plot data
    x = np.arange(len(csi_arr[0]))
    for subc_index in range(0, 4):
        axs[subc_index].plot(x, csi_arr[subc_index])
        axs[subc_index].set_title('subcarrier index ' + tags[subc_index])
    plt.show()


def plot_mad():
    # mad_list = []
    # for i in range(1, 5):
    #     amp, filtered_amp = read_and_filter(sys.argv[i])
    #     # Calculate subcarrier 118 variance
    #     mad_list.append(median_abs_deviation(filtered_amp[118-4][600:1000]))
    # print(mad_list)
    a = np.empty(100)
    a[0:24] = 0.8
    a[24:40] = 3.2
    a[40:50] = 0.8
    a[50:60] = 1.3
    a[60:70] = 0.8
    a[70:80] = 1.9
    a[80:] = 4
    a += ((np.random.rand(100) - 0.5) * 0.8)
    a[20:40] += ((np.random.rand(20) - 0.5) * 2)
    a[80:] += ((np.random.rand(20) - 0.5) * 2)

    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    x = np.arange(100)
    ax.plot(x, a)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.tick_params(axis='both', which='minor', labelsize=18)
    ax.set_xlabel('time', fontsize=22)
    ax.set_ylabel('CSI amp MAD', fontsize=22)

    plt.show()


def plot_var():
    # Idle, walk, sit, wave, run
    # var_list = []
    # for i in range(1, 5):
    #     amp, filtered_amp = read_and_filter(sys.argv[i])
    #     # Calculate subcarrier 118 variance
    #     var_list.append(np.var(filtered_amp[118-4][600:1000]))
    # print(var_list)

    # Test shown that variance are around[2, 20, 5, 6, 20+n]
    a = np.empty(100)
    a[0:24] = 2
    a[24:40] = 20
    a[40:50] = 2
    a[50:60] = 5
    a[60:70] = 2
    a[70:80] = 6
    a[80:] = 26
    a += ((np.random.rand(100) - 0.5) * 2)
    a[20:40] += ((np.random.rand(20) - 0.5) * 14)
    a[80:] += ((np.random.rand(20) - 0.5) * 10)

    plt.style.use('ggplot')
    fig, ax = plt.subplots()
    x = np.arange(100)
    ax.plot(x, a)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.tick_params(axis='both', which='minor', labelsize=18)
    ax.set_xlabel('time', fontsize=22)
    ax.set_ylabel('CSI amp variance', fontsize=22)

    plt.show()


def plot_result():
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots()
    data = [97, 96, 89, 78, 62]
    labels = ['idle', 'walk', 'sit', 'wave', 'run']

    ax.bar(range(len(data)), data, tick_label=labels)
    ax.tick_params(axis='both', which='major', labelsize=18)
    ax.tick_params(axis='both', which='minor', labelsize=18)
    ax.set_xlabel('gait', fontsize=22)
    ax.set_ylabel('Accuracy', fontsize=22)

    for x, y in enumerate(data):
        ax.text(x, y + 1, str(y) + '%', ha='center', fontsize=18)
    plt.show()

def plot_dtw(f1, f2, subc_idx=3):
    with open(f1, 'r') as f:
        for i, line in enumerate(f):
            if i == 3 + subc_idx:
                a1 = np.array([float(v) for v in line.split()])
                print(line)
    with open(f2, 'r') as f:
        for i, line in enumerate(f):
            if i == 3 + subc_idx:
                a2 = np.array([float(v) for v in line.split()])
                print(line)
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(a1)), a1)
    ax.plot(np.arange(len(a2)), a2)
    distance, path = fastdtw(a1, a2, dist=euclidean)
    print(path)
    for pair in path:
        ax.plot(pair, (a1[pair[0]], a2[pair[1]]), 'k--')
    plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename',
                        type=str,
                        dest='filename'
                        )
    parser.add_argument('--file2',
                        type=str,
                        dest='file2'
                        )
    parser.add_argument('-d', '--distance',
                        help='Plot file\'s subcarrier distance',
                        action='store_true',
                        dest='plot_distance'
                        )
    parser.add_argument('--spec-amp',
                        help='Plot specified subcarrier amp, need filename, start_index, end_index, subcarrier_index',
                        action='store_true',
                        dest='plot_spec_subc'
                        )
    parser.add_argument('--start-index',
                        help='CSI start index',
                        type=int,
                        default=0,
                        dest='start_index'
                        )
    parser.add_argument('--stop-index',
                        help='CSI stop index',
                        type=int,
                        default=400,
                        dest='stop_index'
                        )
    parser.add_argument('--subc-index',
                        help='subcarrier_index',
                        nargs='+',
                        default=[45],
                        dest='subc_index'
                        )
    parser.add_argument('--dwt',
                        help='Plot discrete wavelet transform efficients',
                        action='store_true',
                        dest='dwt'
                        )
    parser.add_argument('--result',
                        action='store_true',
                        dest='result'
                        )
    parser.add_argument('--raw',
                        help='process raw CSI data',
                        dest='raw',
                        action='store_true'
                        )
    parser.add_argument('--hampel-only',
                        help='Only use hampel filter',
                        action='store_true',
                        dest='hampel_only'
                        )
    parser.add_argument('--gaussian-sigma',
                        help='Gaussian filter sigma',
                        type=int,
                        dest='gaussian_sigma',
                        default=5
                        )
    parser.add_argument('--result-only',
                        help='Plot only original wave and result when using dwt',
                        action='store_true',
                        dest='result_only'
                        )
    parser.add_argument('--of',
                        help='Output filename',
                        type=str,
                        dest='of'
                        )
    parser.add_argument('--plotline',
                        action='store_true',
                        dest='plotline'
                        )
    parser.add_argument('--plotdtw',
                        action='store_true',
                        dest='plotdtw'
                        )

    args = parser.parse_args()
    if args.plot_distance:
        plot_subc_distance(args.filename)
        exit(0)
    if args.plot_spec_subc:
        plot_spec_subc(args.filename, args.start_index, args.stop_index, args.raw, args.hampel_only, 191)
        exit(0)
    if args.dwt:
        ori_data, dwt_data = discrete_wavelet_transform(args.filename, gaussian_sigma=args.gaussian_sigma,
                                                        result_only=args.result_only)
        if args.of != None:
            with open(args.of, 'w') as f:
                for amp in ori_data:
                    f.write(str(amp))
                    f.write(' ')
                f.write('\n')
                for amp in dwt_data:
                    f.write(str(amp))
                    f.write(' ')
                f.write('\n')
        exit(0)
    if args.result:
        plot_result()
        exit(0)
    if args.plotline:
        plot_line(args.filename)
    if args.plotdtw:
        plot_dtw(args.filename, args.file2)


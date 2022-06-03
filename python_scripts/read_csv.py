#!/usr/bin/env python3

from math import sqrt
from math import atan2
import matplotlib.pyplot as plt
import numpy
import numpy as np
import pywt
from scipy.ndimage import gaussian_filter
import sys
from myLOF import lof
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.stats import median_abs_deviation
from statistics import variance
from os import listdir
from os.path import isfile, join
import random
import argparse


def hampel_filter(subc, window_size=25):
    i = 0
    while i < len(subc) - window_size + 1:
        mdn = np.median(subc[i:i + window_size])
        mad_arr = np.copy(subc[i:i + window_size])
        for j in range(0, len(mad_arr)):
            mad_arr[j] = abs(mad_arr[j] - mdn)
        mad = np.median(mad_arr)
        for k in range(i, i + window_size):
            if abs(subc[k] - mdn) > 3 * 1.4826 * mad:
                subc[k] = mdn
        i += window_size
    if i < len(subc):
        for k in range(i, len(subc)):
            if abs(subc[k] - mdn > 3 * 1.4826 * mad):
                subc[k] = mdn


def cnt_data_len(filename):
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
            if subc_num not in d:
                d[subc_num] = 1
            else:
                d[subc_num] += 1
        print(d)
        print(csi_num)
        plt.style.use('_mpl-gallery')
        fig, ax = plt.subplots()
        x = list(d.keys())
        y = list(d.values())
        x = np.array(x) + 0.5
        ax.bar(x, y, width=1, edgecolor='white', linewidth=0.7)
        ax.set(xlim=(371, 377), xticks=np.arange(372, 379))
        ax.tick_params(axis='both', which='major', labelsize=18)
        ax.tick_params(axis='both', which='minor', labelsize=18)
        ax.set_xlabel('CSI data length', fontsize=22)
        ax.set_ylabel('CSI data num', fontsize=22)

        plt.show()


def read_csv_all_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        csi_num = len(lines)
        # 64 subcarriers * csi_num array
        subc_amplitude = np.zeros((376, csi_num))
        valid_csi_num = 0
        for line in lines:
            l = line.strip('\n')
            l = l.strip('csi_data: ')
            csi_str = l.split(' ')
            # delete data which length less than 376
            if len(csi_str) < 376:
                continue
            i = 0
            while i < 376:
                amp = sqrt(int(csi_str[i]) ** 2 + int(csi_str[i + 1]) ** 2)
                subc_amplitude[int(i / 2)][valid_csi_num] = amp
                i = i + 2
            valid_csi_num = valid_csi_num + 1
    return subc_amplitude[:, :valid_csi_num]


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


def read_and_filter(filename, gaussian_sigma=8):
    subc_amplitude = read_csv_all_data(filename)
    csi_num = len(subc_amplitude[0])
    # remove_outlier(subc_amplitude)
    for subc_index in range(0, 376):
        hampel_filter(subc_amplitude[subc_index])

    # Apply gaussian filter
    filterd_amplitude = np.empty((376, csi_num))
    for i in range(0, 376):
        filterd_amplitude[i] = gaussian_filter(subc_amplitude[i], sigma=gaussian_sigma)
    return subc_amplitude, filterd_amplitude


def scale_point(dir_name, start_seq, scale_base=0):
    f_names = [join(dir_name, f) for f in listdir(dir_name) if isfile(join(dir_name, f))]
    for f_name in f_names:
        with open(f_name, 'r') as f:
            lines = f.readlines()
        out_str = 'csi_data: '
        print(f_name)
        with open(f_name.rstrip('.csv') + '_' + str(start_seq) + '.csv', 'w') as f:
            for line in lines:
                l = line.strip('\n')
                l = l.strip('csi_data: ')
                csi_str = l.split(' ')
                for s_val in csi_str:
                    i_val = int(s_val)
                    noise = ((random.random() * 0.4) + 0.8) + scale_base
                    out_str += str(int(i_val * noise)) + ' '

                f.write(out_str)
                f.write('\n')
                out_str = 'csi_data: '


def process_data(fi, fo):
    raw_amp, flt_amp = read_and_filter(fi)
    """
    Output file structure:
    max45 57 98 118
    mad45 57 98 118
    var45 57 98 118
    dwt_amp45
    dwt_amp57
    dwt_amp98
    dwt_amp118
    """
    feature_list = [[] for i in range(3)]
    subc_index_list = np.array([45, 57, 98, 118]) - 4
    for index in subc_index_list:
        feature_list[0].append(max(flt_amp[index]))
        feature_list[1].append(median_abs_deviation(flt_amp[index]))
        feature_list[2].append(variance(flt_amp[index]))

    coeffs_list = []
    for index in subc_index_list:
        coeffs_list.append(pywt.wavedec(flt_amp[index], 'db1', level=4)[0])

    with open(fo, 'w') as f:
        for feature in feature_list:
            for subc_feature in feature:
                f.write(str(subc_feature))
                f.write(' ')
            f.write('\n')
        for cA in coeffs_list:
            for val in cA:
                f.write(str(val))
                f.write(' ')
            f.write('\n')


def check_processed_data(fi):
    with open(fi, 'r') as f:
        lines = f.readlines()
        cnt = 0
        fig, ax = plt.subplots()
        for line in lines:
            print("Cnt:", cnt)
            v_list = line.split()
            if cnt < 3:
                for v in v_list:
                    print(v)
            else:
                a = np.array([float(v) for v in v_list])
                x = np.arange(len(a))
                ax.plot(x, a, label=str(cnt))
            cnt += 1
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--scale-point',
                        dest='scale_point',
                        action='store_true',
                        default=False
                        )
    parser.add_argument('-f', '--filename',
                        type=str,
                        dest='filename'
                        )
    parser.add_argument('-s', '--seq-num',
                        dest='seq_num',
                        type=int
                        )
    parser.add_argument('-a', '--optional-arg',
                        dest='opt_arg',
                        default=0
                        )
    parser.add_argument('--raw-data',
                        help='Plot raw data without any filter',
                        dest='raw_data',
                        action='store_true'
                        )
    parser.add_argument('--of',
                        help="Output file name",
                        type=str,
                        dest='of'
                        )
    parser.add_argument('-p', '--process-data',
                        help='Calculate data feature and write to a new file',
                        action='store_true',
                        dest='process_data'
                        )
    parser.add_argument('--check',
                        help='Check procesed data',
                        action='store_true',
                        dest='check'
                        )

    args = parser.parse_args()

    if args.scale_point:
        print(float(args.opt_arg))
        folder_name = args.filename
        scale_point(folder_name, args.seq_num, float(args.opt_arg))
    elif args.process_data:
        process_data(args.filename, args.of)
    elif args.check:
        check_processed_data(args.filename)
    # filename = str(sys.argv[1])
    # cnt_data_len(filename)

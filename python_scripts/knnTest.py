#!/usr/bin/env python3

import argparse
import sys

from myknn import calc_distance, read_feature, Action, Distance, calc_dis_btn_train_list, read_dir
from read_csv import read_and_filter
from os import listdir
from os.path import isfile, join
from scipy.stats import median_abs_deviation
from statistics import variance


def compare_distance_list(test_file, test_file_new, train_folder, train_folder_new):
    ori_amps, filtered_amps = read_and_filter(test_file)
    test_act = Action('test_act')
    test_act.actList.append(filtered_amps)
    train_data_list = [read_dir(train_folder, 'train_act')]

    distance_list = [[] for i in range(12)]
    print('Calc_distance')
    calc_distance(test_act, train_data_list, max, 0, distance_list)
    calc_distance(test_act, train_data_list, median_abs_deviation, 1, distance_list)
    calc_distance(test_act, train_data_list, variance, 2, distance_list)

    # New Knn
    train_file_list_new = [join(train_folder_new, f) for f in listdir(train_folder_new) if
                           isfile(join(train_folder_new, f))]
    distance_list_new = [[] for i in range(16)]
    dis_list = calc_dis_btn_train_list(test_file_new, train_file_list_new, False)
    for ft_idx in range(3):
        for subc_idx in range(4):
            for v in dis_list[ft_idx * 4 + subc_idx]:
                distance_list_new[ft_idx * 4 + subc_idx].append(Distance('train_act', v))

    for dis in distance_list:
        dis.sort()
    for dis in distance_list_new:
        dis.sort()

    # print('Old distance_list')
    # for dis in distance_list:
    #     for v in dis:
    #         print(v)
    #
    # print('New distance_list')
    # for dis in distance_list_new:
    #     for v in dis:
    #         print(v)
    for ft_idx in range(3):
        for subc_idx in range(4):
            for dis_idx in range(len(distance_list_new[ft_idx * 4 + subc_idx])):
                if distance_list_new[ft_idx * 4 + subc_idx][dis_idx].dis != distance_list[ft_idx * 4 + subc_idx][
                    dis_idx].dis:
                    print('ft_idx: %s, subc_idx: %s, dis_idx: %s.' % (ft_idx, subc_idx, dis_idx))
    print('Check finish.')


if __name__ == '__main__':
    compare_distance_list(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

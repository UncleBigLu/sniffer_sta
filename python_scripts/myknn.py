#!/usr/bin/env python3

import sys
from os import listdir
from os.path import isfile, join
from read_csv import read_and_filter
from scipy.stats import median_abs_deviation
from statistics import variance


# Usage: python myknn.py <test_data_folder> <test_data_label> <train_data_folder> <train_data_label> [<train_data_folder> <train_data_label>]


class Distance:
    def __init__(self, label, dis):
        self.label = label
        self.dis = dis

    def __lt__(self, other):
        return self.dis < other.dis


class Action:
    def __init__(self, label):
        self.label = label
        self.actList = []


def read_dir(dir_name, label):
    f_names = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]
    action = Action(label)
    for f in f_names:
        subc_amps, filtered_amps = read_and_filter(join(dir_name, f))
        action.actList.append(filtered_amps)
    return action


def calc_distance(test_act, train_data_list, feature_func, feature_idx, dis_list):
    for test_subcs in test_act.actList:
        for train_act in train_data_list:
            for train_subcs in train_act.actList:
                index_idx = 0
                for subc_index in [45 - 4, 57 - 4, 98 - 4, 118 - 4]:
                    test_feature = feature_func(test_subcs[subc_index])
                    train_feature = feature_func(train_subcs[subc_index])
                    dis = Distance(train_act.label, abs(test_feature - train_feature))
                    dis_list[feature_idx * 4 + index_idx].append(dis)
                    index_idx += 1


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage: python myknn.py <test_data_folder> '
              '<test_data_label> <train_data_folder> <train_data_label> [<train_data_folder> <train_data_label>]')
        exit(1)

    test_label = sys.argv[2]
    distance_list = [[] for i in range(12)]

    # Read test data
    test_act = read_dir(sys.argv[1], test_label)

    # Read train datas
    train_data_list = []
    i = 3
    while i < len(sys.argv):
        train_folder = sys.argv[i]
        train_label = sys.argv[i + 1]
        i += 2
        act = read_dir(train_folder, train_label)
        train_data_list.append(act)
    del i

    total_test_num = len(test_act.actList)
    correct_test_num = 0

    # Calculate distances
    # distanceList:[[MAX_SUBC1-4][MAD_SUBC1-4][VAR_SUBC1-4]]
    for test_subcs in test_act.actList:
        test_act_per_file = Action(test_act.label)
        test_act_per_file.actList.append(test_subcs)
        calc_distance(test_act_per_file, train_data_list, max, 0, distance_list)
        calc_distance(test_act_per_file, train_data_list, median_abs_deviation, 1, distance_list)
        calc_distance(test_act_per_file, train_data_list, variance, 2, distance_list)

        for dis in distance_list:
            dis.sort()
        label_cnt = {}
        for dimension in distance_list:
            for dis in dimension[:3]:
                # print(dis.label)
                if dis.label not in label_cnt:
                    label_cnt[dis.label] = 1
                else:
                    label_cnt[dis.label] += 1
        max_cnt = 0
        max_label = ''
        for label in label_cnt:
            if label_cnt[label] > max_cnt:
                max_cnt = label_cnt[label]
                max_label = label
        if max_label == test_label:
            correct_test_num += 1
        else:
            print(max_label)
    print(correct_test_num)
    print(total_test_num)
    print(correct_test_num / total_test_num)

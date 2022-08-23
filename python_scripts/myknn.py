#!/usr/bin/env python3
import os
import sys
from os import listdir
from os.path import isfile, join

import numpy as np

from read_csv import read_and_filter
from scipy.stats import median_abs_deviation
from statistics import variance
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from multiprocessing import Process, Queue


# Usage: python myknn.py <test_data_folder> <test_data_label> <train_data_folder> <train_data_label> [<train_data_folder> <train_data_label>]


def main_backup():
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


class Distance:
    def __init__(self, label, dis):
        self.label = label
        self.dis = dis

    def __lt__(self, other):
        return self.dis < other.dis

    def __str__(self):
        return self.label + ' ' + str(self.dis)

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


def read_feature(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        cnt = 0
        feature_list = [np.empty(4) for i in range(3)]
        dwt_amp = []
        for line in lines:
            v_list = line.split()
            if cnt < 3:
                for i in range(len(v_list)):
                    feature_list[cnt][i] = v_list[i]
            else:
                a = np.array([float(v) for v in v_list])
                dwt_amp.append(a)
            cnt += 1
    return feature_list, dwt_amp


def calc_dis_btn_file(test_file, train_file, dtw_enable=True):
    # print("Test file: " + test_file)
    # print("Train file: " + train_file)
    test_feature_list, test_amp = read_feature(test_file)
    train_feature_list, train_amp = read_feature(train_file)
    feature_distance_list = []
    for ft_idx in range(3):
        feature_distance_list.append(abs(test_feature_list[ft_idx] - train_feature_list[ft_idx]))
    if dtw_enable:
        feature_distance_list.append(np.empty(4))
        for subc_idx in range(4):
            distance, path = fastdtw(test_amp[subc_idx], train_amp[subc_idx], dist=euclidean)
            feature_distance_list[-1][subc_idx] = distance / len(path)

    # print('Get distance')
    return feature_distance_list


def process_task(test_file, train_file_list, queue):
    print('Process pid %s start.' % os.getpid())
    print("Subprocess Running")
    feature_dim = 16
    distance_list = [[] for i in range(feature_dim)]
    for train_file in train_file_list:
        ft_dis_list = calc_dis_btn_file(test_file, train_file)
        for ft_idx in range(4):
            for subc_idx in range(4):
                distance_list[ft_idx * 4 + subc_idx].append(ft_dis_list[ft_idx][subc_idx])

    queue.put(distance_list)
    print('Process pid %s end.' % os.getpid())


def calc_dis_btn_train_list(test_file, train_file_list, dtw_enable=True):
    if dtw_enable:
        feature_dim = 16
        ft_idx_range = 4
    else:
        feature_dim = 12
        ft_idx_range = 3
    distance_list = [[] for i in range(feature_dim)]
    for train_file in train_file_list:
        ft_dis_list = calc_dis_btn_file(test_file, train_file, dtw_enable)
        for ft_idx in range(ft_idx_range):
            for subc_idx in range(4):
                distance_list[ft_idx * 4 + subc_idx].append(ft_dis_list[ft_idx][subc_idx])

    return distance_list


def task_manager(test_file, train_dir):
    train_file_list = [join(train_dir, f) for f in listdir(train_dir) if isfile(join(train_dir, f))]
    distance_list = [[] for i in range(16)]

    p_list = []
    print("Start assign subprocess")
    q = Queue()
    print(q)
    for p_id in range(16):
        p_train_file_list = []
        for i in range(len(train_file_list)):
            if i % 16 == p_id:
                p_train_file_list.append(train_file_list[i])
        p = Process(target=process_task, args=(test_file, train_file_list, q,))
        p_list.append(p)
        p.start()
    print(p_list)

    for i in range(len(p_list)):
        print(p_list[i])
        p_list[i].join()
    print('All process finished.')
    while not q.empty():
        dl = q.get()
        for ft_idx in range(4):
            for subc_idx in range(4):
                distance_list[ft_idx * 4 + subc_idx].append(dl[ft_idx * 4 + subc_idx])
    return distance_list


def get_result(test_file, *args):
    enable_dtw = True
    if enable_dtw:
        ft_idx_range = 4
        dim_num = 16
    else:
        ft_idx_range = 3
        dim_num = 12
    if (len(args) < 2) or (len(args) % 2 != 0):
        print('get_result: Train folder and label error!')
        exit(1)
    arg_cnt = 0
    label_num = len(args)
    label_dis_list = [[] for i in range(dim_num)]
    while arg_cnt < label_num:
        label = args[arg_cnt + 1]
        train_dir = args[arg_cnt]
        # print(train_dir)
        # print(' ')
        arg_cnt += 2
        # dis_list = task_manager(test_file, train_dir)
        train_file_list = [join(train_dir, f) for f in listdir(train_dir) if isfile(join(train_dir, f))]
        # print(train_file_list)
        dis_list = calc_dis_btn_train_list(test_file, train_file_list, enable_dtw)

        for ft_idx in range(ft_idx_range):
            for subc_idx in range(4):
                for v in dis_list[ft_idx*4 + subc_idx]:
                    label_dis_list[ft_idx * 4 + subc_idx].append(Distance(label, v))

    k = 3
    for dis in label_dis_list:
        dis.sort()

    label_cnt = {}
    for dimension in label_dis_list:
        for dis in dimension[:k]:
            # print(dis.label)
            # print(dis)
            if dis.label not in label_cnt:
                label_cnt[dis.label] = 1
            else:
                label_cnt[dis.label] += 1
        # print('')
    max_cnt = 0
    max_label = ''
    for label in label_cnt:
        if label_cnt[label] > max_cnt:
            max_cnt = label_cnt[label]
            max_label = label
    return max_label


def get_accuracy(*args):
    test_dir = args[0]
    test_label = args[1]
    test_file_list = [join(test_dir, f) for f in listdir(test_dir) if isfile(join(test_dir, f))]
    tot_test_num = len(test_file_list)
    crt_test_num = 0
    for test_file in test_file_list:
        label = get_result(test_file, *args[2:])
        if label == test_label:
            crt_test_num += 1
        else:
            print(label)
            print(test_file)
    print(tot_test_num)
    print(crt_test_num)
    print(crt_test_num / tot_test_num)


if __name__ == '__main__':
    get_accuracy(*sys.argv[1:])
    # print(get_result(*sys.argv[1:]))
    # if len(sys.argv) <= 1:
    #     print('Usage: python myknn.py <test_data_folder> '
    #           '<test_data_label> <train_data_folder> <train_data_label> [<train_data_folder> <train_data_label>]')
    #     exit(1)
    #
    # test_label = sys.argv[2]
    # distance_list = [[] for i in range(12)]
    #
    # # Read test data
    # tst_action = Action(test_label)
    # subc_amps, filtered_amps = read_and_filter(sys.argv[1])
    # tst_action.actList.append(filtered_amps)
    #
    # # Read train datas
    # train_data_list = []
    # i = 2
    # while i < len(sys.argv):
    #     train_folder = sys.argv[i]
    #     train_label = sys.argv[i + 1]
    #     i += 2
    #     act = read_dir(train_folder, train_label)
    #     train_data_list.append(act)
    # del i
    #
    #
    #
    # # Calculate distances
    # # distanceList:[[MAX_SUBC1-4][MAD_SUBC1-4][VAR_SUBC1-4]]
    # calc_distance(tst_action, train_data_list, max, 0, distance_list)
    # calc_distance(tst_action, train_data_list, median_abs_deviation, 1, distance_list)
    # calc_distance(tst_action, train_data_list, variance, 2, distance_list)
    #
    # for dis in distance_list:
    #     dis.sort()
    # label_cnt = {}
    # for dimension in distance_list:
    #     for dis in dimension[:3]:
    #         # print(dis.label)
    #         if dis.label not in label_cnt:
    #             label_cnt[dis.label] = 1
    #         else:
    #             label_cnt[dis.label] += 1
    # max_cnt = 0
    # max_label = ''
    # for label in label_cnt:
    #     if label_cnt[label] > max_cnt:
    #         max_cnt = label_cnt[label]
    #         max_label = label
    # print(max_label)
    # # if max_label == test_label:
    # #     correct_test_num += 1
    # # else:
    # #     print(max_label)
    # # print(correct_test_num)
    # # print(total_test_num)
    # # print(correct_test_num / total_test_num)

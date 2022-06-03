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
        self.max_list = []
        self.mad_list = []
        self.var_list = []


def read_dir(dir_name, label):
    f_names = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]
    action = Action(label)
    for f_name in f_names:
        with open(f_name, 'r') as f:
            lines = f.readlines()
        for line in lines[:3]:
            val_list = line.split()

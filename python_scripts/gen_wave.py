import sys
from read_csv import read_and_filter
import numpy as np
import matplotlib.pyplot as plt
import random


def ist_pt(l, num):
    if num == 0 or len(l) == 0:
        return
    l.insert(int(len(l)/2), l[int(len(l)/2 - 1)])
    ist_pt(l[:int(len(l)/2)], int(num-1/2))
    ist_pt(l[int(len(l)/2):], int(num-1/2))


def write_amp(tag, subcs, seq):
    index_list = [45, 57, 98, 118]
    with open('../csi_data/amp/'+str(tag)+'/'+str(seq)+'.csv', 'w') as f:
        for subc_index in index_list:
            amp = subcs[subc_index]
            for i in range(len(amp)):
                f.write(str(amp[i]))
                if(i != len(amp)-1):
                    f.write(' ')
            f.write('\n')


def add_noise(subcs, max_noise = 2):
    index_list = [45, 54, 98, 118]
    subcs_cp = list.copy(subcs)
    for subc_index in index_list:
        for i in range(len(subcs_cp[subc_index])):
            noise = (random.random()-0.5)*2*max_noise
            subcs_cp[subc_index][i] += noise
    return subcs_cp


if __name__ == '__main__':
    tag = sys.argv[1]
    src_file = sys.argv[2]
    start_seq = int(sys.argv[3])
    end_seq = int(sys.argv[4])

    subcs_amplitude, filtered_amplitude = read_and_filter(src_file, gaussian_sigma=8)
    for seq in range(start_seq, end_seq):
        write_amp(tag, filtered_amplitude, seq)



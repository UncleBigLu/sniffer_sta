import numpy as np
from scipy.stats import median_abs_deviation
from read_csv import read_and_filter
import sys

step = 1

if __name__ == '__main__':
    subc_amplitude, filterd_amplitude = read_and_filter(str(sys.argv[1]))
    # calculate variance
    variance = []
    mad = []
    low_point = []
    high_point = []

    for subc_index in range(2, 28, step):
        variance.append(np.var(filterd_amplitude[subc_index]))
        mad.append(median_abs_deviation(filterd_amplitude[subc_index]))

        sort_amp = np.sort(filterd_amplitude[subc_index])
        low_point.append(sort_amp[10])
        high_point.append(sort_amp[-10])

    # print(variance)
    # print(mad)
    # print(low_point)
    # print(high_point)

    with open(str(sys.argv[1]).replace('corrected_data', 'meta_data'), 'w') as f:
        l = [variance, mad, low_point, high_point]
        s = ''
        for i in l:
            for v in i:
                s += str(v)
                s += ' '
            f.write(s)
            f.write('\n')
            s = ''

    np.save(str(sys.argv[1]).replace('corrected_data', 'filterd_data'), filterd_amplitude)

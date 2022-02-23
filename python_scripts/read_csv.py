import re
from math import sqrt
from math import atan2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

re_legalCSI = re.compile(r'^csi_data: (-*\d+ )+$')




with open('../csi_data/csi_chaos_2.csv', 'r') as f:
    lines = f.readlines()
    csi_num = len(lines)
    # 64 subcarriers * csi_num array
    subc_amplitude = np.zeros((64, csi_num))
    subc_phase = np.zeros((64, csi_num))

    valid_csi_num = 0
    for line in lines:
        if(re_legalCSI.match(line)):
            l = line.strip('\n')
            l = l.strip('csi_data: ')
            csi_str = l.split(' ')
            # Observed some csi only contains 120 data, discard them
            if(len(csi_str) < 128):
                continue
            # 64 subcarriers of lltf
            i = 0
            while(i < 128):
                amp = sqrt(int(csi_str[i])**2 + int(csi_str[i+1])**2)
                # atan2(img, real)
                pha = atan2(int(csi_str[i]), int(csi_str[i+1]))
                subc_amplitude[int(i/2)][valid_csi_num] = amp
                subc_phase[int(i/2)][valid_csi_num] = pha
                i = i+2
            valid_csi_num = valid_csi_num + 1

# csi_index = int(input("Please input csi index"))
#
# while(csi_index >= 0):
#     print("amp: "+ str(subc_amplitude[:, csi_index]))
#     csi_index = int(input())


# Apply gaussian filter
filterd_amplitude = np.empty((64, csi_num))
filterd_phase = np.empty((64, csi_num))

for i in range(0, 64):
    filterd_amplitude[i] = gaussian_filter(subc_amplitude[i], sigma=5)
    filterd_phase[i] = gaussian_filter(subc_phase[i], sigma=5)

x = np.arange(csi_num)
for i in range(2, 20):
    plt.plot(x, filterd_amplitude[i], label = "subcarrier "+str(i))

# Calculate covariance between subcarriers
# In this test we calculate cov of lltf subcarriers 2~20
amp_cov = np.zeros(18)
amp_avg = np.zeros(18)

for i in range(2, 20):
    amp_avg[i - 2] = sum(filterd_amplitude[i]) / csi_num
for i in range(0, 17):
    for j in range(0, csi_num):
        amp_cov[i] += (filterd_amplitude[i+2][j] - amp_avg[i])*(filterd_amplitude[i+3][j] - amp_avg[i+1])/csi_num
for j in range(0, csi_num):
    amp_cov[17] += (filterd_amplitude[19][j] - amp_avg[17])*(filterd_amplitude[2][j] - amp_avg[0])/csi_num

print(amp_cov)

plt.legend()
plt.show()

# for i in range(0, 64):
#     x = [j for j in range(0, len(subc_amplitude[i]))]
#     plt.plot(x, subc_phase[i], label="subc"+str(i))
# plt.legend()
# plt.show()









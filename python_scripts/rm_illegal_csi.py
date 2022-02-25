import re

re_legalCSI = re.compile(r'^csi_data: (-*\d+ )+$')

ori_file = '../csi_data/origin_data/csi_idle_1.csv'
corr_file = ori_file.replace('origin_data', 'corrected_data')

with open(ori_file, 'r') as f:
    lines = f.readlines()
    corr_lines = ""
    for line in lines:
        if(re_legalCSI.match(line)):
            l = line.strip('\n')
            l = l.strip('csi_data: ')
            if (l.count(' ') >= 128):
                corr_lines += line
# Write filterd data to a new file
with open(corr_file, 'w') as f:
    f.write(corr_lines)

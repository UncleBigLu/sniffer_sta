import sys
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

amp_file = '../csi_data/filterd_data/'
meta_file = '../csi_data/meta_data/'

gesture_set = ['idle', 'walk', 'sit']

# variance, mad, low_point, high_point
idle_meta = [[],[],[],[]]
walk_meta = [[],[],[],[]]
sit_meta = [[],[],[],[]]

if __name__ == '__main__':
    # Read dataset
    for i in range(70, 74):
        with open(meta_file+'csi_walk_'+str(i)+'.csv', 'r') as f:
            for meta_num in range(0, 4):
                meta = f.readline().split()
                for value in meta:
                    walk_meta[meta_num].append(float(value))

    print(walk_meta)



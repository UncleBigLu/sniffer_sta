import numpy as np

def lof(arr, k=5, w = 20):
    k_dis_arr = np.zeros(len(arr))
    for i in range(0, len(arr)):
        if i < w:
            neighbor_window = np.sort(arr[i:i+w])
        else:
            neighbor_window = np.sort(arr[i-w+1:i+1])

        j, = np.where(neighbor_window == arr[i])
        j = j[0]
        if(j < k):
            k_dis_arr[i] = neighbor_window[j+k] - neighbor_window[j]
        else:
            k_dis_arr[i] = neighbor_window[j] - neighbor_window[j-k]
    return k_dis_arr
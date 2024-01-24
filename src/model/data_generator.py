import pandas as pd
import tensorflow as tf
import numpy as np
from scipy import stats
import os
import scipy
print(scipy.__version__)

# print(tf.__version__)
window_size = 100 # 1
channels = 12 # 后面没有用到

npy_path = '/home/mqiu/hongmin_new/two/npy/window_size100_1/'

# 创建路径
if not os.path.exists(npy_path):
    os.makedirs(npy_path)

def read_folder_of_CSV(directory: str):
    assert os.path.exists(directory)
    #获取文件夹下全部的csv文件名
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    # Initialize an empty list to hold DataFrames
    dataframes = []

    # Loop through the CSV files and read each one into a DataFrame
    for csv_file in csv_files:
        df = pd.read_csv(os.path.join(directory, csv_file))
        #list中的每个元素都是dataframe
        dataframes.append(df)
    # Concatenate all the DataFrames in the list
    # 将'dataframes'列表中的所有DataFrame对象按照行方向（纵向）连接起来，创建一个新的大DataFrame对象，
    # 其中包含了所有CSV文件中的数据。合并后的DataFrame将不保留原始数据帧的索引，并重新生成一个连续的整数索引。
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

def data_generator(X_data, y_data, window_size):
    num_samples, num_features = X_data.shape
    # 间隔是1
    window_nums = num_samples - window_size +1
    gen_x_data = np.zeros((window_nums, window_size, num_features), dtype=np.float16)
    # 一个矩阵是window_size行num_features个，一共有window_nums多个矩阵。
    gen_y_label = []
    for window_index in range(window_nums):
        gen_x_data[window_index, :, :] = X_data[window_index:window_index+window_size, :]
        # X_data（全体数据的纵向拼接）取每一个窗口，大小是window_size*num_features（如500*11）赋值给
        # gen_x_data（三维矩阵），每一个维度都是大小是window_size*num_features的二维矩阵。
        # X_data_demo= X_data[window_index:window_index+window_size, :]
        gen_y_data = np.array(y_data[window_index:window_index+window_size])
        # gen_y_data是一个临时变量，记录每一个窗口的label
        # gen_y_data的是window_size大小的向量
        # print(gen_y_data.shape)
        # mode_info = stats.mode(gen_y_data, keepdims=False, axis=None)
        mode_info = stats.mode(gen_y_data, axis=None)
        # gen_y_data是大小为window_size的一个向量，这样去找它的众数
        # print(mode_info)
        if np.isscalar(mode_info.mode):
            gen_y_label.append(mode_info.mode)
        else:
            gen_y_label.append(mode_info.mode[0])
        # 通过判断众数是否是一个标量（即只有一个众数）来确定要添加到 `gen_y_label` 中的值。
        # 如果众数是标量，则直接添加到 `gen_y_label` 中，否则取众数数组的第一个元素添加到
        # 'gen_y_label'中。
    print(gen_x_data.shape)
    print(len(gen_y_label))
    return gen_x_data, np.array(gen_y_label)

# Read the CSV file
train_data = read_folder_of_CSV('data/labeled_2/train')
# 它选择了从第二列到倒数第二列（即排除第一列和最后一列）的数据，
X_train = train_data.iloc[:, 1:-1].values
# 这一行选择了`train_data`中的最后一列数据，label
y_train = train_data.iloc[:, -1].values
X_train, y_train = data_generator(X_train, y_train, window_size)

val_data = read_folder_of_CSV('data/labeled_2/val')
X_val = val_data.iloc[:, 1:-1].values
y_val = val_data.iloc[:, -1].values
X_val, y_val = data_generator(X_val, y_val, window_size)

test_data = read_folder_of_CSV('data/labeled_2/test')
X_test = test_data.iloc[:, 1:-1].values
y_test = test_data.iloc[:, -1].values
X_test, y_test = data_generator(X_test, y_test, window_size)

# 保存训练集和验证集npy
# train
np.save(npy_path + 'X_train_2.npy', X_train)
np.save(npy_path + 'y_train_2.npy', y_train)
# val
np.save(npy_path + 'X_val_2.npy', X_val)
np.save(npy_path + 'y_val_2.npy', y_val)
# test
np.save(npy_path + 'X_test_2.npy', X_test)
np.save(npy_path + 'y_test_2.npy', y_test)
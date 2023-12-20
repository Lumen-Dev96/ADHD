import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Conv1D, \
    LayerNormalization, BatchNormalization, Activation, MaxPooling1D, Flatten

# 定义模型
def create_model(input_shape: tuple):
    #原始提供
    # model = Sequential()
    # model.add(LayerNormalization(input_shape=input_shape))
    # model.add(Conv1D(16, 3, name='input_conv', use_bias=False))
    # model.add(BatchNormalization())
    # model.add(Activation('relu'))
    # model.add(MaxPooling1D(pool_size=2))
    # model.add(LSTM(16, name='lstm_1'))  # 假设我们有不定长度的序列，每个序列元素是一维的
    # model.add(BatchNormalization())
    # model.add(Activation('relu'))
    # model.add(Dense(14, activation='softmax'))  # 假设我们的分类任务有两类
    # return model

    # Mynetwork
    model = Sequential()
    model.add(Flatten(input_shape=input_shape))  # 将输入展平为一维向量
    model.add(Dense(32, activation='sigmoid'))  # 添加一个全连接层，输出14个类别的概率分布
    model.add(Dense(16, activation='sigmoid'))  # 添加一个全连接层，输出14个类别的概率分布
    model.add(Dense(2, activation='softmax'))  # 添加一个全连接层，输出14个类别的概率分布
    return model

if __name__=='__main__':
    model = create_model(input_shape=(200, 6))
    model.summary()

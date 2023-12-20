#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/11/14 10:23
# @Author  : WANG HONGMIN 
# @Site    : 
# @File    : Algorithm_without_DTW.py
# @Software: PyCharm

import numpy as np
from sklearn.model_selection import train_test_split
import keras
import matplotlib.pyplot as plt
import matplotlib
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Conv1D, Dropout, MaxPooling1D, LSTM, Bidirectional, GRUV1
import tensorflow as tf
import seaborn as sns
from keras.utils import np_utils
from scipy import signal
import sys


raw_data = np.load('data_shoulder_6_channels.npy')

def sample_data(raw_data):
    motion, length, channel = raw_data.shape
    feature_data = np.zeros((motion, channel, 64))
    for i in range(910):
        feature_data[i, :, :] = signal.resample(raw_data[i, :, :].T, 64, axis=1)
    return feature_data

label_data = np.load('label.npy')

feature_data = sample_data(raw_data)
print(feature_data.shape)


def window_slicing(data):
    slice, row, column = data.shape
    num = 64 - 35 + 1
    augmentation_data = np.zeros((slice*num, row, 35))
    for k in range(slice): # 0-727
        for i in range(num): # 0-29
            augmentation_data[k*30+i, :, :] = data[k, :, i:i+35]

    # slice, row = data.shape
    # num = 285 - 256 + 1
    # augmentation_data = np.zeros((slice * num, 256))
    # for k in range(slice): # 0-910
    #     for i in range(num): # 0-29
    #         augmentation_data[k*30+i, :] = data[k, i:i+256]
    return augmentation_data


feature_data = window_slicing(feature_data)  # 扩充30倍数据
print(feature_data.shape)
augmentation_data = np.zeros((300, 256))
x = [i for i in range(50)]



label = []
for i in range(len(label_data)):
    for j in range(30):
        label.append(label_data[i])
label = np.array(label)

print(feature_data.shape)

# sys.exit()
x_train, x_test, y_train, y_test = train_test_split(feature_data, label, test_size=0.2, stratify=label)
print(x_train.shape)
print(x_test.shape)
print(y_train.shape)
print(y_test.shape)
x_train = np.transpose(x_train, (0, 2, 1))
x_test = np.transpose(x_test, (0, 2, 1))

model = Sequential()
nb_class = 14
nb_features = 35

# 一维卷积层用了512个卷积核，输入是64*3的格式
# 1D CNN model
# model.add(Conv1D(64, 3, input_shape=(nb_features, 6)))
# model.add(MaxPooling1D(pool_size=3, strides=2))
# model.add(Activation('relu'))
# model.add(Conv1D(32, 3))
# model.add(MaxPooling1D(pool_size=3, strides=2))
# model.add(Activation('relu'))
# model.add(Conv1D(32, 3))
# model.add(MaxPooling1D(pool_size=3, strides=2))
# model.add(Activation('relu'))
model.add(Flatten())
# model.add(Dense(1536, activation='relu'))
# model.add(Dense(512, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(nb_class, activation='softmax'))

# DNN model
# model.add(Flatten())
# model.add(Dense(768, activation='relu'))
# model.add(Dense(512, activation='relu'))
# model.add(Dense(256, activation='relu'))
# model.add(Dense(128, activation='relu'))
# model.add(Dense(64, activation='relu'))
# model.add(Dense(nb_class, activation='softmax'))

# LSTM model
# n_timesteps, n_features = x_train.shape[1], x_train.shape[2]
# model.add(LSTM(100, input_shape=(n_timesteps, n_features), return_sequences=True))
# model.add(Dropout(0.5))
# model.add(LSTM(100, return_sequences=True))
# model.add(Dropout(0.5))
# model.add(LSTM(100))
# model.add(Flatten())
# # model.add(Dense(768, activation='relu'))
# model.add(Dense(512, activation='relu'))
# model.add(Dense(256, activation='relu'))
# model.add(Dense(128, activation='relu'))
# model.add(Dense(64, activation='relu'))
# model.add(Dense(nb_class, activation='softmax'))


# BiLSTM model
# n_timesteps, n_features = x_train.shape[1], x_train.shape[2]
# # model.add(Bidirectional(LSTM(50, input_shape=(n_timesteps, n_features), return_sequences=True)))
# # model.add(LSTM(15, input_shape=(n_timesteps, n_features), return_sequences=True))
# model.add(tf.keras.layers.SimpleRNN(units=15, activation='relu', input_shape=(n_timesteps, n_features)))
# # model.add(Dropout(0.5))
# # model.add(Bidirectional(LSTM(50, return_sequences=True)))
# # model.add(LSTM(50, return_sequences=True))
# # model.add(Dropout(0.5))
# # model.add(Bidirectional(LSTM(50)))
# # model.add(LSTM(15))
# model.add(Flatten())
# # model.add(Dense(768, activation='relu'))
# # model.add(Dense(512, activation='relu'))
# # model.add(Dense(256, activation='relu'))
# model.add(Dense(32, activation='relu'))
# model.add(Dense(32, activation='relu'))
# model.add(Dense(nb_class, activation='softmax'))

# GRU model
# n_timesteps, n_features = x_train.shape[1], x_train.shape[2]
# model.add(GRUV1(100, input_shape=(n_timesteps, n_features), return_sequences=True))
# model.add(Dropout(0.5))
# model.add(GRUV1(100, return_sequences=True))
# model.add(Dropout(0.5))
# model.add(GRUV1(100))
# model.add(Flatten())
# model.add(Dense(768, activation='relu'))
# model.add(Dense(512, activation='relu'))
# model.add(Dense(256, activation='relu'))
# model.add(Dense(128, activation='relu'))
# model.add(Dense(64, activation='relu'))
# model.add(Dense(nb_class, activation='softmax'))
# model.add(Dense(nb_class, activation='softmax'))
#
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),

              metrics=['sparse_categorical_accuracy'])


history = model.fit(x_train, y_train, batch_size=16, epochs=1, validation_data=(x_test, y_test), validation_freq=1)
model.summary()


###################################################
# edited by Tommy
# 這裡是整個模型的保存，需要以.pb格式提供給我       
# model.save('./model_trained/blilstm')
###################################################

# 评估模型,不输出预测结果
loss, accuracy_train = model.evaluate(x_train, y_train)
loss, accuracy_test = model.evaluate(x_test, y_test)
print('\ntest loss', loss)
print('accuracy', accuracy_test)

yhat_probs = model.predict(x_test, verbose=0)
# predict crisp classes for test set
yhat_classes = np.argmax(yhat_probs, axis=-1)
# reduce to 1d array
yhat_probs = yhat_probs[:, 0]
# yhat_classes = yhat_classes[:, 0]

accuracy = accuracy_score(y_test, yhat_classes)
print('Accuracy: %f' % accuracy)
# precision tp / (tp + fp)
precision = precision_score(y_test, yhat_classes, average='micro')
print('Precision: %f' % precision)
# recall: tp / (tp + fn)
recall = recall_score(y_test, yhat_classes, average='micro')
print('Recall: %f' % recall)
# f1: 2 tp / (2 tp + fp + fn)
f1 = f1_score(y_test, yhat_classes, average='micro')
print('F1 score: %f' % f1)
# confusion matrix
matrix = confusion_matrix(y_test, yhat_classes)
print(matrix)
sns.set(font_scale=1.5)
plt.rc('font',family='Times New Roman',size=12)
sns.heatmap(matrix, cmap="YlGnBu", annot=True)
plt.show()


# 显示训练集和验证集的acc和loss曲线
acc = history.history['sparse_categorical_accuracy']
val_acc = history.history['val_sparse_categorical_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']


# plt.subplot(1, 2, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.title('Model Accuracy')
plt.legend()
plt.show()


# plt.subplot(1, 2, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.title('Model Loss')
plt.legend()
plt.show()






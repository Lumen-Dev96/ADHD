import tensorflow
from tensorflow import keras
from keras.models import Sequential
import numpy as np
from scipy import signal
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 
# model = Sequential()

# print(type(model))

model = keras.models.load_model('model_trained/blilstm')
print(type(model))

model.summary()

# predictions = model.predict(x_test[:3])
# model

# # Generate predictions (probabilities -- the output of the last layer)
# # on new data using `predict`
# print("Generate predictions for 3 samples")
# predictions = model.predict(x_test[:3])
# print("predictions shape:", predictions.shape)


raw_data = np.load('data_shoulder_6_channels.npy')

def sample_data(raw_data):
    motion, length, channel = raw_data.shape
    feature_data = np.zeros((motion, channel, 64))
    for i in range(910):
        feature_data[i, :, :] = signal.resample(raw_data[i, :, :].T, 64, axis=1)
    return feature_data

label_data = np.load('label.npy')

feature_data = sample_data(raw_data)

feature_data = np.transpose(feature_data, (0, 2, 1))


input = feature_data[0][:35]

for line in input:
    print('[',line[0],',',line[1],',',line[2],',',line[3],',',line[4],',',line[5],'],',)

input = np.array([input])

predictions = model.predict(input)
print(predictions)
import numpy as np
import pandas as pd
from J_network import create_model
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import Adam
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

window_size = 100
channels = 12
epochs = 10 #5

# 结果路径
result_path = './result/'

#数据路径
npy_path = './data/'

# train
X_train = np.load(npy_path + 'X_train_2.npy')
y_train = np.load(npy_path + 'y_train_2.npy')
# val
X_val = np.load(npy_path + 'X_val_2.npy')
y_val = np.load(npy_path + 'y_val_2.npy')
# test
X_test = np.load(npy_path + 'X_test_2.npy')
y_test = np.load(npy_path + 'y_test_2.npy')

# # 使用SVD分解将矩阵进行压缩
# svd = TruncatedSVD(n_components=10)
# X_train_compressed = svd.fit_transform(X_train.reshape(X_train.shape[0], -1))
# X_val_compressed = svd.transform(X_val.reshape(X_val.shape[0], -1))
# X_test_compressed = svd.transform(X_test.reshape(X_test.shape[0], -1))

model = create_model(input_shape=(window_size, channels))

model.compile(optimizer='adam', loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False), metrics='accuracy')

checkpoint = ModelCheckpoint(result_path + 'test.pb', monitor='val_loss', mode='min', save_best_only=True, verbose=1)
model.fit(X_train, y_train, batch_size=32, epochs=epochs, validation_data=(X_val, y_val), callbacks=[checkpoint])

#------------------------模型评价阶段----------------------------
# 使用训练好的模型在训练集上进行评估
train_loss, train_accuracy = model.evaluate(X_train, y_train)
# 使用训练好的模型在测试集上进行评估
test_loss, test_accuracy = model.evaluate(X_test, y_test)
# 打印训练集的误差和精度
print(f'Train Loss: {train_loss}')
print(f'Train Accuracy: {train_accuracy}')
# 打印测试集的误差和精度
print(f'Test Loss: {test_loss}')
print(f'Test Accuracy: {test_accuracy}')
# 使用训练好的模型进行预测
y_pred = model.predict(X_test)
# 将预测结果转换为类别标签
y_pred_labels = np.argmax(y_pred, axis=1)
# 计算精确度、召回率和F1分数
precision = precision_score(y_test, y_pred_labels, average='weighted')
recall = recall_score(y_test, y_pred_labels, average='weighted')
f1 = f1_score(y_test, y_pred_labels, average='weighted')

y_test = y_test.astype(np.int64)
# y_pred_labels = y_pred_labels.astype(np.int64)
# my_test_loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)(tf.convert_to_tensor(y_test), tf.convert_to_tensor(y_pred_labels))

# 计算准确度
my_test_accuracy = accuracy_score(tf.convert_to_tensor(y_test), tf.convert_to_tensor(y_pred_labels))

# 打印手动计算得到的损失值和准确度
# print(f'Manual Loss: {my_test_loss}')
print(f'Manual Accuracy_test: {my_test_accuracy}')

# 打印精确度、召回率和F1分数
print(f'Precision_test: {precision}')
print(f'Recall_test: {recall}')
print(f'F1 Score_test: {f1}')

# 计算混淆矩阵
confusion_mat = confusion_matrix(y_test, y_pred_labels)
labels = np.unique(np.concatenate((y_train, y_test)))
# sns.heatmap(confusion_mat, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
# 不敢相信！center = 0！center：浮点数，可选参数。绘制有色数据时将色彩映射居中的值。 如果没有指定，则使用此参数将更改默认的cmap
sns.heatmap(confusion_mat, annot=True, fmt='g', cmap ='Blues', center = 0, xticklabels=labels, yticklabels=labels)


plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()
plt.savefig(result_path + 'Confusion Matrix.png')

# 生成分类报告
class_report = classification_report(y_test, y_pred_labels, output_dict=True)
# 打印分类报告
print('Classification Report:')
print(class_report)
print(type(class_report))
# 保存分类报告
df = pd.DataFrame(class_report).transpose()
df.to_csv(result_path + 'class_report.csv', index= True)

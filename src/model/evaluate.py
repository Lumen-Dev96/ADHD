from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix
import seaborn as sns
import sys

window_size = 30
result_path = './result/'

# 加载模型
model = load_model('../server/pb/test30_1.pb')
# 假设我们有一个新的数据集 X_new，它是一个形状为 (num_samples, num_features) 的二维数组
new_data = pd.read_csv(r'../server/output.csv')

# scaler = MinMaxScaler()
X_new = new_data.iloc[:, 1:].values
# X_new = scaler.fit_transform(X_new)

y_new = new_data.iloc[:, -1].values
num_samples, num_features = X_new.shape

# 初始化一个空列表来保存预测结果
predictions = []

# num_samples-window_size
# 遍历数据集中的每一个窗口
for i in range(num_samples-window_size):
    # 提取当前窗口的数据
    X_window = X_new[i:i + window_size, :]

    X_window = X_window[np.newaxis, ...]

    # 使用模型进行预测
    y_pred = model.predict(X_window)

    print(y_pred)
    # 将预测结果添加到列表中
    predictions.append(y_pred)

# 将预测结果转换为 NumPy 数组
predictions = np.concatenate(predictions, axis=0)
# print(predictions)
# 提取预测类别的最大概率
predicted_classes = np.argmax(predictions, axis=1)
# print(predicted_classes)

# 遍历数据集中的每一个窗口，找到每个窗口的众数
mode_labels = [stats.mode(y_new[i:i + window_size])[0] for i in range(num_samples - window_size)]
# 将结果转换为 NumPy 数组，ravel()是一个NumPy数组的方法，它将任何形状的数组转换为一维数组
mode_labels = np.array(mode_labels).ravel()

# 使用 matplotlib 绘制预测类别的折线图
plt.figure(figsize=(14, 6))

# 绘制预测类别
plt.plot(predicted_classes, label='Predicted Classes')
# 绘制真实类别
plt.plot(mode_labels, label='True Classes')
plt.title('Predicted vs True Classes')
plt.xlabel('Time Step')
plt.ylabel('Class')
plt.legend()
plt.show()
plt.savefig(result_path + 'Predicted vs True Classes_12_1.png')

# 计算混淆矩阵
cm = confusion_matrix(mode_labels, predicted_classes)

# 绘制混淆矩阵的热图
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d',center = 0, cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('True')
plt.show()
plt.savefig(result_path + 'Confusion Matrix_12_1.png')
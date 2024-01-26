from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import layout
from bokeh.io import push_notebook, show, output_notebook
import numpy as np
from tensorflow.keras.models import load_model
import sys
import pandas as pd
import paho.mqtt.client as mqtt
import json
import datetime
import socket
import threading
import re
import matplotlib.pyplot as plt
import time
from math import *




def transformTimestamps(timestamp):
    # d = datetime.datetime.fromtimestamp(timestamp/1000)
    # time_str = d.strftime("%Y-%m-%d %H:%M:%S.%f")
    transform_time = timestamp + 946656000
    date = datetime.datetime.fromtimestamp(transform_time)
    time_str = date.strftime('%Y-%m-%d %H:%M:%S')
    return time_str

# 更新函數，每次呼叫時更新數據
def update(message):
    global x, y_data, grap_id, x_record, rawData, record_count, max_data_count, stop_time_seconds
    
    # 解碼 MQTT 數據
    # payload = message.payload.decode()
    # data = json.loads(payload)

    # test mode
    data = message

    
    mqData = np.array(data)
    # fifoData = np.array(data[1])


    times = mqData[:, 0]
    channel1 = mqData[:, 1]
    channel2 = mqData[:, 2]
    channel3 = mqData[:, 3]
    channel4 = mqData[:, 4]
    channel5 = mqData[:, 5]
    channel6 = mqData[:, 6]
    channel7 = mqData[:, 7]
    channel8 = mqData[:, 8]
    channel9 = mqData[:, 9]
    channel10 = mqData[:, 10]
    channel11 = mqData[:, 11]
    channel12 = mqData[:, 12]

    

    # 将时间戳转换为本地时间元组
    # new_times = np.vectorize(transformTimestamps)(times)
    # print('times:', new_times)

    rawData.append(mqData)


    
    # 使用模型进行预测
    ranges = np.array([[1.7, 2], [6.7, 7], [-7, -6.6], [-4, 2], [-2, 2], [-8, -3], [0, 0.3], [9, 9.3], [-4.3, -4], [0, 5], [-2, 2], [-6, -4]])
    # 使用 numpy.random.uniform 生成具有不同範圍的數據
    dataForTest = np.column_stack([np.random.uniform(low=low, high=high, size=30) for low, high in ranges])
    print('-----------------')
    dataForTest = dataForTest[np.newaxis, ...]
    print('transforming test random data shape:', dataForTest.shape)

    # 使用訓練數據展示結果
    dataForTrain = trained_data_x[record_count * data_length : record_count * data_length + data_length, :]
    dataForTrain = dataForTrain[np.newaxis, ...]
    print('transforming train data shape:', dataForTrain.shape)
    # print('data for train:', dataForTrain)

    # fifoData = np.delete(fifoData, 0, axis=1)
    # print('fifo;', fifoData)
    # fifoData = fifoData[np.newaxis, ...]
    # print('transforming fifo data shape:', fifoData.shape)
    # y_pred = model.predict(fifoData)

    # predictions.append(y_pred[0])
    # print('predictions:', predictions)
    # print('------------------')

    # # 将预测结果转换为 NumPy 数组
    # predictionsNp = np.array(predictions)
    # print('predictoinNp:', predictionsNp)
    # print('------------------')
    # print('predictions shape:', predictionsNp.shape)
    # print(predictionsNp)
    # # 提取预测类别的最大概率 >0.5 => 1, <0.5 => 0
    # predicted_classes = predictionsNp[-1]
    # print(predicted_classes)
    # # 只會有一個結果, 值為 0 或者 1
    # print(predicted_classes[0])
    # prediction_label = round(predicted_classes[0])
    # print('predicted_classes', predicted_classes)
    # print('prediction_label', prediction_label)
    x_record += 1
    # source13.stream({'x':np.arange(x_record, x_record + 1), 'y':[prediction_label]})


    # 更新數據源的數據
    grap_id += data_length

    record_count = record_count + 1

    times_arr.append(times[0])


    # plt.clf() # 清空画布上的所有内容。此处不能调用此函数，不然之前画出的点，将会被清空。
    plt.sca(mpu1)    
    plt.plot(times, channel1, label='AX1', color="orange")
    plt.plot(times, channel2, label='AY1', color="purple")
    plt.plot(times, channel3, label='AZ1', color="green")
    plt.plot(times, channel4, label='GX1', color="red")
    plt.plot(times, channel5, label='GY1', color="blue")
    plt.plot(times, channel6, label='GZ1', color="grey")
    plt.pause(0.01)#注意此函数需要调用

    print(channel1)


    plt.sca(mpu2)    
    plt.plot(times, channel7, label='AX2', color="orange")
    plt.plot(times, channel8, label='AY2', color="purple")
    plt.plot(times, channel9, label='AZ2', color="green")
    plt.plot(times, channel10, label='GX2', color="red")
    plt.plot(times, channel11, label='GY2', color="blue")
    plt.plot(times, channel12, label='GZ2', color="grey")
    plt.pause(0.01)#注意此函数需要调用







def exportCSV():
    global rawData
    csvData = np.concatenate(rawData, axis=0)
    timestamps = csvData[:, 0]
    ax1 = csvData[:, 1]
    ay1 = csvData[:, 2]
    az1 = csvData[:, 0]
    gx1 = csvData[:, 7]
    gy1 = csvData[:, 8]
    gz1 = csvData[:, 9]

    ax2 = csvData[:, 4] 
    ay2 = csvData[:, 5]
    az2 = csvData[:, 6]
    gx2 = csvData[:, 10]
    gy2 = csvData[:, 11]
    gz2 = csvData[:, 12]

    # 将时间戳转换为本地时间元组
    new_times = np.vectorize(transformTimestamps)(timestamps)

    # dictionary of lists
    dict = {'Time': new_times, 'Ax1': ax1, 'Ay1': ay1, 'Az1': az1, 'Gx1': gx1, 'Gy1': gy1, 'Gz1': gz1, 'Ax2': ax2, 'Ay2': ay2, 'Az2': az2, 'Gx2': gx2, 'Gy2': gy2, 'Gz2': gz2}
        
    df = pd.DataFrame(dict)
    filename = 'output.csv'
    df.to_csv(filename, index=False)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, message):
    print("Received data from esp32 via MQTT")
    update(message)
    # print("Received message on topic %s: %s" % (message.topic, message.payload.decode()))



def broadcast(command):
    """ Send a command to all connected clients. """
    with clients_lock:  # Acquire lock to ensure list is not modified while iterating
        for client in clients:
            try:
                client.send(command.encode('utf-8'))  # Send the command to each client
            except socket.error as e:  # Handle potential socket errors
                print(f'Error sending to client: {e}')

def client_thread(client_socket, client_address):
    global data_buffer
    """ Handle communication with a connected client. """
    print(f'New connection from {client_address}') # used to check the connection is created or not
    # Add the new client to the clients list in a thread-safe manner
    with clients_lock:
        clients.append(client_socket)
    try:
        while True:  # Continuously receive data from the client
            imu_data = client_socket.recv(164000).decode('utf-8')

            print(imu_data)
            imu_json = json.loads(imu_data)

            if imu_json['func'] == 'log':
                print('message from ESP32: ', imu_json['msg'])
            elif imu_json['func'] == 'visualization':
                update(imu_json['data'])
            # if not imu_data :  # If no data is received, it means the client has disconnected
            #     break
            # elif Special_Command == "Real_Time_Detection":
            #     # print('Receiving data:', imu_data)
            #     update([imu_data])
            #     data_buffer.append(imu_data)
            # else:

            # Here you could call broadcast() if needed

    except socket.error as e:  # Handle any exceptions that occur within the thread
        print(f'Error with client {client_address}: {e}')
    finally:
        # When the client disconnects, remove it from the clients list and close the socket
        with clients_lock:
            clients.remove(client_socket)
        client_socket.close()
        print(f'Connection with {client_address} closed')

def connect_mqtt_server():
    # 连接MQTT代理
    # broker_address = "broker.emqx.io"
    broker_address = "127.0.0.1"
    # broker_address = "broker.mqttdashboard.com"
    # broker_address = "test.mosquitto.org"
    port = 1883
    username = "ESP32_Monitor"
    password = "123"

    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message


    client.connect(broker_address, port)

    # 订阅消息
    client.subscribe(topic)

    client.loop_forever()

def broadcast_thread():
    global Special_Command
    global save_file_path
    global Running_IMU
    global data_buffer
    global Buffer_of_IMU2
    """ Thread function for broadcasting commands at regular intervals. """
    while True:
        # Send a command to all clients
        command_code = input('Input the command for IMU:\n 1 - List All Directory \n 2 - Update Local Time \n 3 - Print Local Time \n 4 - Start Collecting \n 5 - Stop Collecting \n 6 - Connect MQTT Server \n 7 - Export CSV \n 0 - Quit \n')
        
        if command_code == '0':
            message = '{}: {}'.format(nickname, 'stop')
            broadcast(message)
            close_sockets()
        elif command_code == '1':
            message = '{}: {}'.format(nickname, 'listdirectory')
            broadcast(message)
        elif command_code == '2':
            # add the timestamp from the PC and
            message = nickname+":"+"Update_Local_Time_as"+ datetime.datetime.now().strftime("%Y-%m-%d-1-%H-%M-%S-%f")[:-3]
            broadcast(message)
        elif command_code == '3':
            message = '{}: {}'.format(nickname, 'Check_IMU_Time')
            broadcast(message)
        elif command_code == '4':
            Special_Command = "Real_Time_Detection"
            message = '{}: {}'.format(nickname, 'Real_time_Detection_and_Save_as')
            broadcast(message)
        elif command_code == '5':
            if len(data_buffer) > 0 and len(Buffer_of_IMU2) > 0:
                print(len(data_buffer),len(Buffer_of_IMU2))
                Special_Command = ""
                save_file_path = ""
                Running_IMU = None
            message = '{}: {}'.format(nickname, 'stop')# input the command from the console
            broadcast(message)
        elif command_code == '6':
            connect_mqtt_server()
        elif command_code == '7':
            save_recieved_data(data = data_buffer, file_path = save_file_path)
        else:
            print('Invalid Command, please try again.')
            Special_Command = ""
            save_file_path = ""
            Running_IMU = None





# 初始化數據/設定
data_length = 30

data_channels = 12

x = np.arange(data_length)

y_data = [np.zeros(data_length) for _ in range(data_channels + 1)]

grap_id = 0

record_count = 0

rawData = []

topic = "AD1"

max_data_count = 10000

stop_time_seconds = 100

trained_data = pd.read_csv('../../public/data/csv/a1_1.csv')
trained_data_x = trained_data.iloc[:, 1:-1].values

times_arr = []

########### LOAD MODEL ###############
# 初始化一个空列表来保存预测结果
predictions = []
model_path = '../../public/pb/test30_1.pb'
x_record = 1
model = load_model(model_path)
########### LOAD MODEL ###############




plt.ion() #开启interactive mode 成功的关键函数
t = [0]
t_now = 0
m = [sin(t_now)]

plt.figure(figsize=(18, 10.8), dpi=100)


#第一行第一列图形
mpu1 = plt.subplot(2,1,1)
#第一行第二列图形
mpu2 = plt.subplot(2,1,2)

           
plt.sca(mpu1)       
plt.title("MPU1", fontsize=15)
plt.xlabel("Timestamp", fontsize=13)
plt.ylabel("Sensor", fontsize=13)
plt.xticks(rotation=90)
mpu_y_ticks = np.arange(-50, 50, 1)
plt.yticks(mpu_y_ticks)

plt.sca(mpu2)    
plt.title("MPU2", fontsize=15)
plt.xlabel("Timestamp", fontsize=13)
plt.ylabel("Sensor", fontsize=13)
plt.xticks(rotation=90)
mpu_y_ticks = np.arange(-50, 50, 1)
plt.yticks(mpu_y_ticks)


test_mode = True
# connect_mqtt_server()

while test_mode:
    test_data = []
    for i in range(30):
        test_data.append([
            time.time(), 
            1.0123,
            1.012,
            1.0123,
            1.0123,
            1.0123,
            1.0123,
            1.0123,
            -20.0123,
            1.0123,
            1.0123,
            10.0123,
            1.0123,
        ])
    update(test_data)
    time.sleep(0.5)


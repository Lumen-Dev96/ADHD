# import serial

# ser = serial.Serial('/dev/tty.usbserial-1420', 115200)  # 请根据你的串口配置调整参数

# while True:
#     print('receving...')
#     data_received = ser.read(1024).decode('utf-8').strip()
#     print(data_received)
#     if ser.in_waiting :
#         print("Received from MicroPython:", data_received)
#     else :
#         print("error")

# ser.close()

# encoding=utf-8
import serial
import time

if __name__ == '__main__':
    com = serial.Serial('/dev/cu.usbserial-1420', 115200)
    over_time = 30
    start_time = time.time()
    while True:
        end_time = time.time()
        if end_time - start_time < over_time:
            data = com.read(com.inWaiting())
            data = str(data)
            if data != '':
                print(data)
from ADHD_model_lite import MyModel
import gc
import time 
import machine
from mpu6050 import MPU6050

uart = machine.UART(0, baudrate=115200, tx=17, rx=16)  # 请根据你的硬件配置调整参数
fifo = []
counter = [1]

def fill_fifo():
    processed_data1 = process_data(mpu1.get_data(True))
    processed_data2 = process_data(mpu2.get_data(True))
    processed_data = processed_data1 + processed_data2
    del processed_data1
    del processed_data2
    gc.collect()

    if len(fifo) >= FIFO_SIZE:
        tmp = fifo.pop(0)
        del tmp
        gc.collect()
    fifo.append(processed_data)
    # fifo.append(processed_data1)


def mpu_fifo_data():
    if counter[0] >= 32:
        fill_fifo()
        counter_1 = 1
    else:
        counter_1 = counter[0] + 1
    counter.append(counter_1)
    counter_0 = counter.pop(0)
    del counter_0
    gc.collect()
    

def process_data(mpudata):
    mpu_data_list = []
    mpu_data_list.append(mpudata.get('accelX'))
    mpu_data_list.append(mpudata.get('accelY'))
    mpu_data_list.append(mpudata.get('accelZ'))
    mpu_data_list.append(mpudata.get('gyroX'))
    mpu_data_list.append(mpudata.get('gyroY'))
    mpu_data_list.append(mpudata.get('gyroZ'))

    return mpu_data_list

#主处理函数
def main():
    # 初始化两个传感器    
    iic = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
    mpu1 = MPU6050(iic, 104)
    mpu2 = MPU6050(iic, 105)
    print(mpu1, mpu2)

    # 初始化定时器，每 10ms 进入中断线程采集数据
    timer_collecting = machine.Timer(0)
    timer_collecting.init(period=10, callback=lambda t:mpu_fifo_data())

    while True:
        if len(fifo) < 10:
            continue
        else:
            data_to_send = fifo
            uart.write(data_to_send)
            del data_to_send
            time.sleep(3)
            gc.collect()


        

if __name__ == '__main__':
    main()

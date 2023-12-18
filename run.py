from ADHD_model_lite import MyModel
import gc
import time 
import machine
from mpu6050 import MPU6050

# machine.freq(240000000)

def fill_fifo():
    processed_data = process_data(mpu1.get_data(True))
    if len(fifo) >= FIFO_SIZE:
        tmp = fifo.pop(0)
        del tmp
        gc.collect()
    fifo.append(processed_data)


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


fifo = []
counter = [1]
FIFO_SIZE = 35

if __name__ == '__main__':
    # 初始化两个传感器    
    iic = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
    mpu1 = MPU6050(iic, 104)
    mpu2 = MPU6050(iic, 105)
    print(mpu1, mpu2)

    # 初始化定时器，每 10ms 进入中断线程采集数据
    timer_collecting = machine.Timer(0)
    timer_collecting.init(period=10, callback=lambda t:mpu_fifo_data())
    
    print('fifo loading')
    while True:
        if len(fifo) < FIFO_SIZE:
            continue
        else:
            # 开始运行模型
            model = MyModel(fifo)
            model.run_model()
            print('-----')
            del model
            time.sleep(0.5)
            gc.collect()
            print('-----')
        
        

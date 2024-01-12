# from ADHD_model_lite import MyModel
import gc
import time 
import machine
from mpu6050 import MPU6050
from umqtt_simple import MQTTClient
import _thread
import sd_card
import json
import network
import micropython
from vibrator import VIBRATOR
from kalman import KALMAN

# machine.freq(240000000)
machine.freq(80000000)

def fill_fifo():
    processed_data = process_data(mpu1.get_data(True), mpu2.get_data(True))
    
    if len(fifo) >= FIFO_SIZE:
        tmp = fifo.pop(0)
        del tmp
        gc.collect()
    fifo.append(processed_data)
    rawData.append(processed_data)
    del processed_data
    gc.collect()
    # fifo.append(processed_data1)


def mpu_fifo_data():   
    fill_fifo()

    # if counter[0] >= 32:
    #     fill_fifo()
    #     counter_1 = 1
    # else:
    #     counter_1 = counter[0] + 1
    # counter.append(counter_1)
    # counter_0 = counter.pop(0)
    # del counter_0
    # gc.collect()
    

def process_data(mpudata1, mpudata2):
    mpu_data_list = []

    ax1 = ax1_filter.get_A(mpudata1.get('accelX'))
    ay1 = ay1_filter.get_A(mpudata1.get('accelY'))
    az1 = az1_filter.get_A(mpudata1.get('accelZ'))

    gx1 = gx1_filter.get_G(mpudata1.get('gyroX'))
    gy1 = gy1_filter.get_G(mpudata1.get('gyroY'))
    gz1 = gz1_filter.get_G(mpudata1.get('gyroZ'))

    ax2 = ax2_filter.get_A(mpudata2.get('accelX'))
    ay2 = ay2_filter.get_A(mpudata2.get('accelY'))
    az2 = az2_filter.get_A(mpudata2.get('accelZ'))

    gx2 = gx2_filter.get_G(mpudata2.get('gyroX'))
    gy2 = gy2_filter.get_G(mpudata2.get('gyroY'))
    gz2 = gz2_filter.get_G(mpudata2.get('gyroZ'))

    mpu_data_list = [ax1, ay1, az1, gx1, gy1, gz1, ax2, ay2, az2, gx2, gy2, gz2]

    # print('KALMAN Filter:', mpu_data_list)

    return mpu_data_list

#WiFi连接函数
def wifi_connect():
    print('Start WIFI Module')
    wlan=network.WLAN(network.STA_IF)#STA模式
    wlan.active(False)#先进行wlan的清除
    wlan.active(True)#再激活 - !注意 這裡可能斷電重啟,激活wlan模塊需要穩定電壓
    start_time=time.time()#记录时间做超时判断
    
    if not wlan.isconnected():
        print("connecting to network…")
        wlan.connect(ssid,password)#输入WiFi账号和密码
        while not wlan.isconnected():
            wifi_led.value(1)
            time.sleep_ms(300)
            wifi_led.value(0)
            time.sleep_ms(300)
            #超时判断，30s未连接成功判定为超时
            if time.time()-start_time>30:
                print("WiFi Connect TimeOut!")
                break
    
    if wlan.isconnected():
        wifi_led.value(1)
        print("network information:",wlan.ifconfig())
        return True
    

#数据采集及主题发布函数
def publish_readSensorData(client, clientID):

    while True:
        # 周期数据采集
        global deviceGetTime, rawData
        if flagUploadData == True:          
            #设置周期采集数据 单位s
            time.sleep(deviceGetTime)
            mpu_fifo_data()
            # 发布主题，主题内容为获取到的传感器的数据
            # print(len(rawData))
            if len(rawData) >= MQTT_SIZE:
                print('Publishing Sensor Data...')
                print('Sleeping... waiting for receive data')
                time.sleep(3)
                mqtt_msg = json.dumps([fifo, rawData])
                client.publish(topic='AD4', msg=mqtt_msg, qos=0, retain=False)
                del mqtt_msg
                del rawData
                gc.collect() 
                rawData = []           
        else:
            time.sleep(2)
            print('当前网络异常，停止上传数据')


# 主题订阅处理函数
def sub_cb(topic, msg):
    #print(topic, msg)
    # 申明全局变量
    global deviceGetTime
    if topic.decode("utf-8") == "EditTime" :
        #data = json.loads(msg)
        print ("data['deviceGetTime']: ", json.loads(msg)['deviceGetTime'])
        deviceGetTime = json.loads(msg)['deviceGetTime']
        

#主处理函数
def main():

    # 看門狗
    wdt = machine.WDT(timeout=10000)
    wdt.feed()
    
    if wifi_connect():
        #申明全局变量
        global mqttHost,mqttPort,keepalive,flagUploadData,flagThread,clientID,userName,userPassword,deviceGetTime
        flagUploadData = True
        clientID = "202308242357838"
        deviceGetTime = 0.01 # 初始化设备采样周期

        client = MQTTClient(clientID, mqttHost, mqttPort, userName, userPassword, keepalive)  # 建立一个MQTT客户端
        #client.set_callback(sub_cb)  # 设置回调函数
        client.connect()  # 建立连接
        #client.subscribe(b"EditTime")  # 订阅EditTime主题
        micropython.mem_info()


        ax1_filter.__int__()
        ay1_filter.__int__()
        az1_filter.__int__()
        gx1_filter.__int__()
        gy1_filter.__int__()
        gz1_filter.__int__()

        ax2_filter.__int__()
        ay2_filter.__int__()
        az2_filter.__int__()
        gx2_filter.__int__()
        gy2_filter.__int__()
        gz2_filter.__int__()

        
        if flagThread == True:
            _thread.start_new_thread(publish_readSensorData, (client,clientID))# 开启线程发布主题及内容
            flagThread=False

        while True:
            wdt.feed()
            # client.check_msg()
            time.sleep(0.05)

            # if len(fifo) < FIFO_SIZE:
            #     continue
            # else:
            #     # 开始运行模型
            #     model = MyModel(fifo)
            #     model.run_model()
            #     print('--- Model Start ---')
            #     # print('DATA:')
            #     # print(fifo)
            #     del model
            #     time.sleep(0.5)
            #     gc.collect()
            #     print('--- Model End ----')
            

if __name__ == '__main__':
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        machine.deepsleep(0x7FFFFFFF)
    print('_________Start program_________')
    print(time.localtime())

    print('memory check:')
    micropython.mem_info()


    """    全局配置开始    """
    # 數據採集參數
    fifo = []
    rawData = []
    counter = [1]
    FIFO_SIZE = 30
    MQTT_SIZE = 30
    # sd卡
    # sd = machine.SDCard(slot=1, width=4, freq=40_000_000)
    # 全局配置WiFi连接参数
    ssid = 'IoT'
    password = 'eduhk+IoT+2018'
    # ssid = 'top'
    # password = 'lzj61271056'
    # 全局配置mqtt连接参数
    mqttHost = "broker.emqx.io" # MQTT代理服务器地址 这里使用公用的MQTT服务器做测试
    # mqttHost = "broker.mqttdashboard.com"
    # mqttHost = "test.mosquitto.org"
    mqttPort = 1883 #端口
    keepalive = 60 #保活时间 单位s
    clientID = 1
    userName ="lumen" #客户端的用户名
    userPassword = 'pwd123456' #客户端用户密码
    flagThread=True #设置一个标志位 默认设备上电只开启一个线程，设备断网重连后不开启新的线程
    flagUploadData = False #设置一个标志位 判断是否断网 决定是否上传数据
    deviceGetTime = 10 #设备周期采集时间

    # 卡爾曼濾波器
    ax1_filter = KALMAN()
    ay1_filter = KALMAN()
    az1_filter = KALMAN()
    gx1_filter = KALMAN()
    gy1_filter = KALMAN()
    gz1_filter = KALMAN()

    ax2_filter = KALMAN()
    ay2_filter = KALMAN()
    az2_filter = KALMAN()
    gx2_filter = KALMAN()
    gy2_filter = KALMAN()
    gz2_filter = KALMAN()

    # 创建WiFi连接指示LED对象
    wifi_led = machine.Pin(19, machine.Pin.OUT, value=0)
    # 创建震動控制
    vibrator = VIBRATOR(machine.Pin(21, machine.Pin.OUT, value=0))

    # 初始化两个传感器    
    iic = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
    mpu1 = MPU6050(iic, 104)
    mpu2 = MPU6050(iic, 105)
    """    全局配置结尾    """


    # 初始化定时器，每 10ms 进入中断线程采集数据
    # timer_collecting = machine.Timer(0)
    # timer_collecting.init(period=10, callback=lambda t:mpu_fifo_data())

    print('fifo loading')
    print(mpu1, mpu2)
    # print('SD Card:', sd_card.check(sd))
    
    main()
        
        

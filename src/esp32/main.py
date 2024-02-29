import network
import utime
import machine
from mpu6050 import MPU6050
import _thread
from vibrator import VIBRATOR
import gc
import ujson
import uarray
from umqtt_simple import MQTTClient


def all_mpu_init():
    global mpu_is_ok
    if mpu1.init() and mpu2.init():
        mpu_is_ok = True
        print('MPU is init success')
    else:
        mpu_is_ok = False
        print('MPU is init failed')


def collecting(t):
    global data_cnt, collecting_cnt, rawData
    if mpu_is_ok:
        mpu_data1 = mpu1.get_data(is_open_gyro)
        mpu_data2 = mpu2.get_data(is_open_gyro)

        # # 坐标轴和方向映射转换
        rawData.append([
            utime.time(),
            mpu_data1['accelX'],
            mpu_data1['accelY'],
            mpu_data1['accelZ'],
            mpu_data1['gyroX'],
            mpu_data1['gyroY'],
            mpu_data1['gyroZ'],

            mpu_data2['accelX'],
            mpu_data2['accelY'],
            mpu_data2['accelZ'],
            mpu_data2['gyroX'],
            mpu_data2['gyroY'],
            mpu_data2['gyroZ']
        ])

        # uarray.array('f', [
        #     utime.time(),
        #     mpu_data1['accelX'],
        #     mpu_data1['accelY'],
        #     mpu_data1['accelZ'],
        #     mpu_data1['gyroX'],
        #     mpu_data1['gyroY'],
        #     mpu_data1['gyroZ'],

        #     mpu_data2['accelX'],
        #     mpu_data2['accelY'],
        #     mpu_data2['accelZ'],
        #     mpu_data2['gyroX'],
        #     mpu_data2['gyroY'],
        #     mpu_data2['gyroZ']
        # ])

        # print(rawData)


        del mpu_data1, mpu_data2
        gc.collect()

        data_cnt += 1
        collecting_cnt += 1

        if collecting_cnt % 1000 == 0:
            print(collecting_cnt, ' data collected')

        if auto_stop and collecting_cnt >= auto_stop_cnt:
            stop_collect()
            vibrator.start([0.12, 0.15, 0.12])
            utime.sleep_ms(500)
    else:
        stop_collect()
        vibrator.start([0.12, 0.15, 0.12])
        utime.sleep(500)



#数据采集及主题发布函数
def publish_sensor_data(client, clientID):
    global data_cnt, rawData
    while is_collecting:
        if len(rawData) > 0 and len(rawData) % BATCH_SIZE == 0:
            data_cnt = 0
            client.publish(topic='ADHD', msg=ujson.dumps(rawData), qos=0, retain=False)
            rawData.clear()
            gc.collect()
        pass

def start_collect():
    global is_collecting, collecting_cnt, data_cnt
    timer_collecting.deinit()
    machine.freq(240000000)
    all_mpu_init()
    if mpu_is_ok:
        collecting_cnt = 0
        data_cnt = 0
        led.on()
        print('Start Collecting')
        is_collecting = True
        timer_collecting.init(period=10, callback=collecting)
        try:
            _thread.start_new_thread(publish_sensor_data, (mqtt_client, MQTT_CLIENT_ID))# 开启线程发布主题及内容
        except:
            print('无法开启线程')
    else:
        machine.freq(80000000)
        print('mpu not loaded')
        utime.sleep(500)

def stop_collect():
    global is_collecting, sdcard_is_ok
    timer_collecting.deinit()
    machine.freq(80000000)

    led.off()
    is_collecting = False
    print('Stop Collecting... We have collected', data_cnt)
    utime.sleep_ms(150)


# Handling Command from remote control
# def command_listener(client):
#     global rtc

#     Command = client.recv(1024).decode()
#     Command = Command.split(":")
#     if len(Command) >= 2 :
        
#         Command = Command[1]
        
#         Command = Command.replace(" ", "")
#     else:
#         Command = "invalid commnad"
    
#     print("Recieved: ", Command)

#     if Command == "Check_IMU_Time":
#         tcp_send(json.dumps({"func":"log", "msg":"Local Time: " + str(rtc.datetime())}))
#     elif "Real_time_Detection_and_Save_as" in Command:
#         if not is_collecting:
#             start_collect()
#         else:
#             tcp_send(json.dumps({"func":"log", "msg":'already collecting data...'}))
    
#     elif "Update_Local_Time_as" in Command:
#         Current_Time = Command.split("as")[1]
#         if Current_Time != "":
#             print("Current time from pc is ",Current_Time)
#             date_list = Current_Time.split("-")
#             date = (int(date_list[0]), int(date_list[1]), int(date_list[2]),int(date_list[3]), int(date_list[4]), int(date_list[5]),int(date_list[6]),int(date_list[7]+"000"))
#             rtc.datetime(date)
#             tcp_send(json.dumps({"func":"log", "msg":"Now IMU time is " + str(rtc.datetime())}))
            
#     elif Command == "stop":
#         stop_collect()
#         tcp_send(json.dumps({"func":"log", "msg":"Collecting stop..."}))

#     elif Command == "listdirectory":
#         tcp_send(json.dumps({"func":"log", "msg":'List all the file within the SD card'}))
#         for txtfile  in os.listdir('/sd/mpuData') :
#             if txtfile.endswith(".txt") :
#                 tmp = 'sd/mpuData/' + txtfile
#                 tcp_send(json.dumps({"func":"log", "msg":"IMU1 has " + tmp}))
#     else:
#         print('Invalid Command')

                    

#WiFi连接函数
def wifi_connect():
    print('Start WIFI Module')
    wlan = network.WLAN(network.STA_IF)#STA模式
    wlan.active(False)#先进行wlan的清除
    wlan.active(True)#再激活 - !注意 這裡可能斷電重啟,激活wlan模塊需要穩定電壓
    start_time = utime.time()#记录时间做超时判断

    if not wlan.isconnected():
        print("connecting to network…")
        wlan.connect(SSID, SSID_PASS)#输入WiFi账号和密码
        while not wlan.isconnected():
            led.value(1)
            utime.sleep_ms(300)
            led.value(0)
            utime.sleep_ms(300)
            #超时判断，30s未连接成功判定为超时
            if utime.time() - start_time > 30:
                print("WiFi Connect TimeOut!")
                break
    
    if wlan.isconnected():
        led.value(1)
        print("network information:", wlan.ifconfig())
        return True
       

#日誌主题发布函数
def log(message):    
    mqtt_client.publish(topic='Log', msg=ujson.dumps(message), qos=0, retain=False)
    print('Log:', message)

# 主题订阅处理函数
def sub_cb(topic, msg):
    #print(topic, msg)
    if topic.decode("utf-8") == "Command" :
        command = ujson.loads(msg)
        print ("Received command: ", command)
        if command == 'vibrator':
            vibrator.start([0.12, 0.15])
            log('Hyper action detected.')
        elif command == 'start_collect':
            if not is_collecting:
                vibrator.start([0.15])
                start_collect()
                log('Start collecting...')
            else:
                log('Is collecting, can not start again.')
        elif command == 'stop_collect':
            if not is_collecting:
                log('No collecting thread.')
            else:
                stop_collect()
                log('Stop collecting....')

            

   


def main():

    # 看門狗
    # wdt = machine.WDT(timeout=20000)
    # wdt.feed()

    if wifi_connect():

        mqtt_client.set_callback(sub_cb)  # 设置訂閱回调函数
        mqtt_client.connect()  # 建立连接
        mqtt_client.subscribe(b"Command")  # 订阅主题

        if not is_collecting:
            vibrator.start([0.15])
            start_collect()
            

        while True:
            # wdt.feed()
            mqtt_client.wait_msg()
            utime.sleep_ms(1000)


        
if __name__ == '__main__':
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        machine.deepsleep(0x7FFFFFFF)
    print('_________Start program_________')

    """    全局配置开始    """
    # sd = machine.SDCard(slot=1, width=4, freq=40_000_000)

    iic = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
    mpu1 = MPU6050(iic, 104)
    mpu2 = MPU6050(iic, 105)
    
    led = machine.Pin(19, machine.Pin.OUT, value=0)

    vibrator = VIBRATOR(machine.Pin(21, machine.Pin.OUT, value=0))
    
    is_open_gyro = True
    auto_stop = False
    auto_stop_cnt = 30000
    
    is_collecting = False

    mpu_is_ok = False
    sdcard_is_ok = False
    deviceGetTime = 10 #设备周期采集时间
    rtc = machine.RTC()
    timer_collecting = machine.Timer(0)

    collecting_cnt = 0 # 紀錄已採集的數據量
    data_cnt = 0 # 紀錄當前批次的數據集大小, 用於觸發發布數據後的歸0處理, 避免內存不夠
    rawData = []

    BATCH_SIZE = 50
    # SERVER_IP = '172.19.251.201'
    SERVER_IP = '172.19.252.224'
    # SERVER_IP = '172.20.10.7' # My PC ip 
    SERVER_PORT = 10000  # The port the server is listening on
    SSID = 'IoT'
    SSID_PASS = 'eduhk+IoT+2018'

    MQTT_PORT = 1883 #端口
    MQTT_KEEP_ALIVE = 60 #保活时间 单位s
    MQTT_CLIENT_ID = 'ESP32'
    MQTT_USER_NAME ="ESP32" #客户端的用户名
    MQTT_USER_PASS = 'pwd123456' #客户端用户密码
    mqtt_client = MQTTClient(MQTT_CLIENT_ID, SERVER_IP, MQTT_PORT, MQTT_USER_NAME, MQTT_USER_PASS, MQTT_KEEP_ALIVE)
    
    print(str(rtc.datetime()))
    """    全局配置结尾    """

    # do not used sd card, it takes too much memory        
    # sdcard_is_ok = sd_card.check(sd)

    main()

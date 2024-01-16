import machine
from mpu6050 import MPU6050
import os
import socket
import network
import time
import _thread
import json
import other
import sd_card
import time_lib
from vibrator import VIBRATOR
from kalman import KALMAN

machine.freq(80000000)


def all_mpu_init():
    global mpu_is_ok
    if mpu1.init() and mpu2.init():
        mpu_is_ok = True
        print('MPU is init success')
        if is_open_warn:
            open_mpu_interrupt(1)
    else:
        mpu_is_ok = False
        print('MPU is init failed')
    if is_connect_app:
        if mpu_is_ok:
            tcp_send('{\"func\":\"MpuInitOK\"}')
        else:
            tcp_send('{\"func\":\"MpuInitError\"}')
        print('Send mpu status to app')


def open_mpu_interrupt(t):
    global warn_delay, is_open_warn
    if not is_collecting:
        warn_delay = 60
        threshold = int(0.2552 * flash_config['threshold'] + 0.7448)
        if threshold > 0xFF:
            threshold = 0xFF
        mpu1.open_INT(threshold)
        mpu2.open_INT(threshold)
        mpu1.set_mode('cycle')
        mpu2.set_mode('cycle')
        print('set mode:cycle')
        is_open_warn = True


def close_mpu_interrupt(t):
    global is_open_warn
    is_open_warn = False
    mpu1.close_INT()
    mpu2.close_INT()
    if not is_collecting:
        mpu1.set_mode('sleep')
        mpu2.set_mode('sleep')
        print('set mode:sleep')


def check_threshold():
    global warn_delay
    if not vibrator.is_working:
        data1 = mpu1.get_INT_status()
        data2 = mpu2.get_INT_status()

        if (data1[0] | data2[0]) & 0x40 == 0x40 and warn_delay == 0:
            warn_delay = int(flash_config['shakeTime'] / 1000.0 + 4) * 20
            print('Threshold is Warning')
            vibrator.start([flash_config['shakeTime'] / 1000.0])


def collecting(t):
    global txt_cnt, line_list, collecting_cnt
    if sdcard_is_ok:
        mpu_data1 = mpu1.get_data(flash_config['isOpenGyro'])
        mpu_data2 = mpu2.get_data(flash_config['isOpenGyro'])

        # # 坐标轴和方向映射转换
        data1 = {'AX': mpu_data1['accel' + flash_config['mapX']] * flash_config['mapXDirect'],
                 'AY': mpu_data1['accel' + flash_config['mapY']] * flash_config['mapYDirect'],
                 'AZ': mpu_data1['accel' + flash_config['mapZ']] * flash_config['mapZDirect'],
                 'GX': mpu_data1['gyro' + flash_config['mapX']] * flash_config['mapXDirect'],
                 'GY': mpu_data1['gyro' + flash_config['mapY']] * flash_config['mapYDirect'],
                 'GZ': mpu_data1['gyro' + flash_config['mapZ']] * flash_config['mapZDirect']}

        data2 = {'AX': mpu_data2['accel' + flash_config['mapX']] * flash_config['mapXDirect'],
                 'AY': mpu_data2['accel' + flash_config['mapY']] * flash_config['mapYDirect'],
                 'AZ': mpu_data2['accel' + flash_config['mapZ']] * flash_config['mapZDirect'],
                 'GX': mpu_data2['gyro' + flash_config['mapX']] * flash_config['mapXDirect'],
                 'GY': mpu_data2['gyro' + flash_config['mapY']] * flash_config['mapYDirect'],
                 'GZ': mpu_data2['gyro' + flash_config['mapZ']] * flash_config['mapZDirect']}

        time_array = time.localtime()
        line = '%02d%02d_%02d%02d%02d\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f' % (time_array[1], time_array[2], time_array[3], time_array[4], time_array[5], data1['AX'], data1['AY'], data1['AZ'], data2['AX'], data2['AY'], data2['AZ'])
        if flash_config['isOpenGyro']:
            line += '\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f' % (data1['GX'], data1['GY'], data1['GZ'], data2['GX'], data2['GY'], data2['GZ'])

        # time_array = time.localtime()
        # line = '%02d%02d_%02d%02d%02d\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f' % (time_array[1], time_array[2], time_array[3], time_array[4], time_array[5], mpu_data1['accelX'], mpu_data1['accelY'], mpu_data1['accelZ'], mpu_data2['accelX'], mpu_data2['accelY'], mpu_data2['accelZ'])
        # if flash_config['isOpenGyro']:
        #     line += '\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f' % (mpu_data1['gyroX'], mpu_data1['gyroY'], mpu_data1['gyroZ'], mpu_data2['gyroX'], mpu_data2['gyroY'], mpu_data2['gyroZ'])
        line_list.append(line + '\r\n')

        #  卡尔曼滤波
        data1['AX'] = ax1_filter.get_A(data1['AX'])
        data1['AY'] = ay1_filter.get_A(data1['AY'])
        data1['AZ'] = az1_filter.get_A(data1['AZ'])
        data2['AX'] = ax2_filter.get_A(data2['AX'])
        data2['AY'] = ay2_filter.get_A(data2['AY'])
        data2['AZ'] = az2_filter.get_A(data2['AZ'])

        if flash_config['isOpenGyro']:
            data1['GX'] = gx1_filter.get_G(data1['GX'])
            data1['GY'] = gy1_filter.get_G(data1['GY'])
            data1['GZ'] = gz1_filter.get_G(data1['GZ'])
            data2['GX'] = gx2_filter.get_G(data2['GX'])
            data2['GY'] = gy2_filter.get_G(data2['GY'])
            data2['GZ'] = gz2_filter.get_G(data2['GZ'])

        line = '%02d%02d_%02d%02d%02d\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f' % (time_array[1], time_array[2], time_array[3], time_array[4], time_array[5], data1['AX'], data1['AY'], data1['AZ'], data2['AX'], data2['AY'], data2['AZ'])
        if flash_config['isOpenGyro']:
            line += '\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f' % (data1['GX'], data1['GY'], data1['GZ'], data2['GX'], data2['GY'], data2['GZ'])
        filter_line_list.append(line + '\r\n')
        # 卡尔曼滤波完成

        txt_cnt += 1
        collecting_cnt += 1
        if is_open_warn and collecting_cnt % 40 == 0:
            check_threshold()
        if is_connect_app and collecting_cnt % 1000 == 0:
            pub_json = {'func': 'log', 'msg': '已采集%d条数据...' % collecting_cnt}
            try:
                _thread.start_new_thread(tcp_send, (json.dumps(pub_json),))
            except:
                pass
        if flash_config['autoStop'] and collecting_cnt >= flash_config['autoStopCnt']:
            stop_collect()
            vibrator.start([0.12, 0.15, 0.12])
            time.sleep(0.5)
    else:
        stop_collect()
        vibrator.start([0.12, 0.15, 0.12])
        time.sleep(0.5)


def data_deal_thread(t):
    global txt_cnt
    while is_collecting:
        if txt_cnt >= 20 and sdcard_is_ok:
            txt_cnt = 0
            txt_str = ''.join(line_list)
            line_list.clear()
            data_file.write(txt_str)

            txt_str = ''.join(filter_line_list)
            filter_line_list.clear()
            filter_file.write(txt_str)
            del txt_str
        pass


def start_collect():
    global data_filename, is_collecting, sdcard_is_ok, data_file, collecting_cnt, txt_cnt, filter_file
    timer_collecting.deinit()
    machine.freq(240000000)
    if sdcard_is_ok:
        data_file = None
        line_list.clear()
        filter_line_list.clear()
        try:
            os.mount(sd, '/sd')
            if time.time() < 722990370:
                (config, sdcard_is_ok) = sd_card.read_config()
                sdcard_is_ok = sd_card.write_config(str(config + 1))

                data_filename = 'MPU_%08d' % config
            else:
                data_filename = 'MPU_' + time_lib.get_format_date()
            sdcard_is_ok = sd_card.add_data_file(data_filename + '.txt', flash_config['isOpenGyro'])
            sdcard_is_ok = sd_card.add_data_file(data_filename + '_filter.txt', flash_config['isOpenGyro'])
            data_file = open('/sd/mpuData/' + data_filename + '.txt', 'a')
            filter_file = open('/sd/mpuData/' + data_filename + '_filter.txt', 'a')
        except OSError:
            sdcard_is_ok = False
            if data_file is not None:
                data_file.close()

        if sdcard_is_ok:
            all_mpu_init()
            if mpu_is_ok:
                collecting_cnt = 0
                txt_cnt = 0
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
                if is_connect_app:
                    tcp_send(json.dumps({'func': 'log', 'msg': '数据采集中...'}))
                led.on()
                print('start collect')
                is_collecting = True
                timer_scan.init(period=50, mode=machine.Timer.ONE_SHOT, callback=key_scan)
                timer_collecting.init(period=10, callback=collecting)
                try:
                    _thread.start_new_thread(data_deal_thread, (1,))
                except:
                    print('无法开启线程')
            else:
                data_file.close()
                os.umount('/sd')

                machine.freq(80000000)
                if is_connect_app:
                    tcp_send(json.dumps({'func': 'MpuInitError'}))

                vibrator.start([0.12, 0.15, 0.12])
                time.sleep(0.5)
        else:
            machine.freq(80000000)
            if is_connect_app:
                tcp_send(json.dumps({'func': 'sdCardError'}))
            vibrator.start([0.12, 0.15, 0.12])
            time.sleep(0.5)
    else:
        machine.freq(80000000)
        if is_connect_app:
            tcp_send(json.dumps({'func': 'sdCardError'}))
        vibrator.start([0.12, 0.15, 0.12])
        time.sleep(0.5)


def stop_collect():
    global is_collecting, sdcard_is_ok
    timer_collecting.deinit()
    if sdcard_is_ok:
        try:
            data_file.write(''.join(line_list))
            data_file.close()
            filter_file.write(''.join(filter_line_list))
            filter_file.close()
            os.umount('/sd')
            line_list.clear()
            filter_line_list.clear()
        except:
            sdcard_is_ok = False
            if data_file is not None:
                data_file.close()
    if not sdcard_is_ok and is_connect_app:
        tcp_send(json.dumps({'func': 'sdCardError'}))
    machine.freq(80000000)
    if is_open_warn:
        try:
            _thread.start_new_thread(open_mpu_interrupt, (1,))
        except:
            print('无法开启线程')
    else:
        mpu1.set_mode('sleep')
        mpu2.set_mode('sleep')
    led.off()
    is_collecting = False
    print('stop collect')
    if is_connect_app:
        time.sleep_ms(150)

        tcp_send(json.dumps({'func': 'log', 'msg': '数据采集完成'}))


def tcp_send(msg: str):
    global is_connect_app
    try:
        listen_socket.send(msg)
    except:
        is_connect_app = False


def network_ap_mode():
    global wifi_mode, ap
    ap.active(True)
    wifi_mode = 2
    print('WiFi mode: AP')


def check_power():
    global power_percent
    adc_value = adc.read_uv() / 1000
    if adc_value > adc_max:
        adc_value = adc_max
    if adc_value < adc_min:
        adc_value = adc_min
    percent = int((adc_value - adc_min) * 100 / (adc_max - adc_min) + 0.5)
    print("power:%d%%" % percent)
    if power_percent != percent:
        power_percent = percent
        if is_connect_app:
            try:
                buffer = '{\"func\":\"powerPercent\",\"data\":%d}' % percent
                tcp_send(buffer)
            except OSError:
                pass
    if percent <= 0:
        print('电量过低，已睡眠')
        vibrator.start([0.12, 0.15, 0.12, 0.15, 0.12])
        mpu1.set_mode('sleep')
        mpu2.set_mode('sleep')
        time.sleep(0.9)
        machine.deepsleep(0x7FFFFFFF)


def timer_1s_task():
    global ap_null_time, wifi_mode, adc_time, is_connect_app, sleep_time_cnt
    if not is_collecting and wifi_mode == 2:
        if ap.isconnected():
            ap_null_time = 300
        else:
            ap_null_time -= 1
            is_connect_app = False
        if ap_null_time == 0:
            listen_socket.close()
            ap.active(False)
            wifi_mode = 0
            is_connect_app = False
            print('已关闭AP热点')
    adc_time -= 1
    if adc_time == 0:
        adc_time = 60
        check_power()
    if wifi_mode == 0 and not is_collecting and not is_open_warn:
        sleep_time_cnt -= 1
        if sleep_time_cnt == 0:
            print('长时间未操作，已睡眠')
            vibrator.start([0.12, 0.15, 0.12, 0.15, 0.12])
            mpu1.set_mode('sleep')
            mpu2.set_mode('sleep')
            time.sleep(0.9)
            machine.deepsleep(0x7FFFFFFF)
    else:
        sleep_time_cnt = 30


def accept_handler(sck: socket.socket):
    client, addr = sck.accept()
    print(addr, 'connected')
    client.setsockopt(socket.SOL_SOCKET, 20, process_handler)


def deal_command(command_json, sck):
    global is_open_warn, change_warn_flag
    func = command_json['func']
    if func == 'StartCollect':
        if not is_collecting:
            start_collect()
    elif func == 'StopCollect':
        if is_collecting:
            stop_collect()
    elif func == 'openWarn':
        if not is_collecting:
            data = command_json['threshold']
            other.update_flash_config(flash_config, {'threshold': data})
            change_warn_flag = 2
    elif func == 'closeWarn':
        if not is_collecting:
            change_warn_flag = 1
    elif func == 'Connection':
        if not sdcard_is_ok:
            sck.send(json.dumps({'func': 'sdCardError'}))
        else:
            sck.send(json.dumps({'func': 'sdCardOK'}))
            if not mpu_is_ok:
                sck.send(json.dumps({'func': 'MpuInitError'}))

            send_data = {'func': 'warnStatus', 'status': is_open_warn}
            sck.send(json.dumps(send_data))

            send_data = {'func': 'isOpenGyro', 'status': flash_config['isOpenGyro']}
            sck.send(json.dumps(send_data))

            send_data = {'func': 'autoStop', 'status': flash_config['autoStop'], 'autoStopCnt': flash_config['autoStopCnt']}
            sck.send(json.dumps(send_data))

            send_data = {'func': 'powerPercent', 'data': power_percent}
            sck.send(json.dumps(send_data))

    elif func == 'updateShakeTime':
        data = command_json['data']
        other.update_flash_config(flash_config, {'shakeTime': data})
    elif func == 'getShakeTime':
        send_data = {'func': 'shakeTime', 'data': flash_config['shakeTime']}
        sck.send(json.dumps(send_data))
    elif func == 'getThreshold':
        send_data = {'func': 'threshold', 'data': flash_config['threshold']}
        sck.send(json.dumps(send_data))
    elif func == 'mpuInit':
        if not is_collecting:
            all_mpu_init()
    elif func == 'updateTime':
        time_lib.update_local_time(command_json['time'])
    elif func == 'autoStop':
        flash_config['autoStop'] = command_json['status']
        if flash_config['autoStop']:
            flash_config['autoStopCnt'] = command_json['autoStopCnt']
        other.update_flash_config(flash_config, flash_config)
    elif func == 'isOpenGyro':
        other.update_flash_config(flash_config, {'isOpenGyro': command_json['status']})
    elif func == 'setCoordMap':
        flash_config['mapX'] = command_json['mapX']
        flash_config['mapY'] = command_json['mapY']
        flash_config['mapZ'] = command_json['mapZ']
        flash_config['mapXDirect'] = command_json['mapXDirect']
        flash_config['mapYDirect'] = command_json['mapYDirect']
        flash_config['mapZDirect'] = command_json['mapZDirect']
        other.update_flash_config(flash_config, flash_config)
    elif func == 'getCoordMap':
        send_data = {'func': 'coordMap', 'mapX': flash_config['mapX'], 'mapY': flash_config['mapY'], 'mapZ': flash_config['mapZ'], 'mapXDirect': flash_config['mapXDirect'], 'mapYDirect': flash_config['mapYDirect'], 'mapZDirect': flash_config['mapZDirect']}
        sck.send(json.dumps(send_data))


def process_handler(sck: socket.socket):
    global is_connect_app, listen_socket
    data = sck.recv(1024)
    if data:
        print(data)
        listen_socket = sck
        is_connect_app = True
        command_json = json.loads(data)
        try:
            _thread.start_new_thread(deal_command, (command_json, sck))
        except:
            print('无法开启线程')


def create_tcp_server():
    try:
        listen_socket.bind((tcpIP, tcpPort))  # bind ip and port
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set the value of the given socket option
        listen_socket.setsockopt(socket.SOL_SOCKET, 20, accept_handler)
        listen_socket.listen(1)  # listen message
    except:
        vibrator.start([0.3])
        if listen_socket:
            try:
                listen_socket.close()
            except:
                pass


def key_scan(t):
    global wifi_mode, is_open_warn, is_connect_app, is_collecting, sleep_time_cnt
    key = '0'
    if connect_key.value() == 0:
        key = 'C'
        sleep_time_cnt = 900
    elif start_key.value() == 0:
        sleep_time_cnt = 900
        key = 'S'
    if key_property['old'] == 'C' and key == '0' and key_property['cnt'] < 15 and wifi_mode != 2:
        # 短按连接按键
        network_ap_mode()  # 设置ESP8266_AP模式相关参数
        time.sleep(0.5)
        is_connect_app = False
        create_tcp_server()
        print('已打开AP热点')
        vibrator.start([0.15])
        if is_collecting:
            stop_collect()

    elif key_property['old'] == 'C' and key == 'C' and key_property['cnt'] == 15 and wifi_mode == 2:
        # 长按连接按键
        is_connect_app = False
        vibrator.start([0.15])
        listen_socket.close()
        time.sleep(0.8)
        print("关闭AP热点")
        ap.active(False)
        wifi_mode = 0
        if is_collecting:
            stop_collect()
    elif key_property['old'] == 'S' and key == '0' and key_property['cnt'] < 15:
        second_key_down = 50
        while second_key_down != 0 and start_key.value() == 1:
            second_key_down -= 1
            time.sleep(0.01)
        if second_key_down == 0:
            # 单击开始按键
            if not is_open_warn and not is_collecting:
                print("开启提醒功能,阈值:%d" % flash_config['threshold'])
                open_mpu_interrupt(1)
                if is_connect_app:
                    send_data = {'func': 'warnStatus', 'status': is_open_warn}
                    tcp_send(json.dumps(send_data))
                vibrator.start([0.15])
                time.sleep(0.2)
        else:  # 双击
            if not is_collecting:
                vibrator.start([0.15])
                time.sleep(0.2)
                while start_key.value() == 0:
                    pass
                start_collect()
            else:
                while start_key.value() == 0:
                    pass
    elif key_property['old'] == 'S' and key == 'S' and key_property['cnt'] == 15:
        # 长按
        if is_open_warn:
            close_mpu_interrupt(1)
            print("关闭提醒功能")
            if is_connect_app:
                send_data = {'func': 'warnStatus', 'status': is_open_warn}
                tcp_send(json.dumps(send_data))
        if is_collecting:
            stop_collect()
        vibrator.start([0.22])
        time.sleep(0.27)
    key_property['old'] = key
    if key == '0':
        key_property['cnt'] = 0
    else:
        key_property['cnt'] += 1
        if key_property['cnt'] > 20:
            key_property['cnt'] = 20
    if is_collecting:
        timer_scan.init(period=50, mode=machine.Timer.ONE_SHOT, callback=key_scan)


if __name__ == '__main__':
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        machine.deepsleep(0x7FFFFFFF)
    print('_________Start program_________')
    print(time.localtime())

    """    全局配置开始    """
    AP_SSID = '动作分析设备'  # WiFi名称
    AP_PASS = '1234567890'  # WiFi密码
    tcpIP = '192.168.4.1'  # TCP的IP地址
    tcpPort = 31415  # TCP端口
    listen_socket = socket.socket()  # create socket
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=AP_SSID, password=AP_PASS, authmode=3, max_clients=1)
    ap.active(False)
    wifi_mode = 0
    ap_null_time = 300

    is_open_warn = False
    change_warn_flag = 0
    warn_delay = 0
    is_connect_app = False
    is_collecting = False

    sd = machine.SDCard(slot=1, width=4, freq=40_000_000)
    sdcard_is_ok = True
    flash_config = {'threshold': 20, 'shakeTime': 300, 'isOpenGyro': False, 'autoStop': False, 'autoStopCnt': 30000,
                    'mapX': 'X', 'mapXDirect': 1, 'mapY': 'Y', 'mapYDirect': 1, 'mapZ': 'Z', 'mapZDirect': 1}

    iic = machine.SoftI2C(scl=machine.Pin(17), sda=machine.Pin(16), freq=400000)
    mpu1 = MPU6050(iic, 104)
    mpu2 = MPU6050(iic, 105)
    mpu1.set_mode('sleep')
    mpu2.set_mode('sleep')
    mpu_is_ok = False
    timer_collecting = machine.Timer(0)
    collecting_cnt = 0
    txt_cnt = 0
    data_filename = ''
    data_file = None
    filter_file = None
    line_list = []
    filter_line_list = []
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

    led = machine.Pin(19, machine.Pin.OUT, value=0)

    vibrator = VIBRATOR(machine.Pin(21, machine.Pin.OUT, value=0))

    adc = machine.ADC(machine.Pin(34))
    adc_time = 1
    adc_max = 865
    adc_min = 590
    power_percent = 100

    connect_key = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)
    start_key = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    key_property = {'old': '0', 'cnt': 0}
    sleep_time_cnt = 30
    task_cnt = 0
    timer_scan = machine.Timer(1)
    """    全局配置结尾    """

    led.off()
    check_power()
    other.read_flash_config(flash_config)
    print('flash_config:', flash_config)
    all_mpu_init()
    sdcard_is_ok = sd_card.check(sd)
    task_cnt = 0
    led.on()
    vibrator.start([0.15])
    time.sleep(0.2)
    led.off()
    wdt = machine.WDT(timeout=10000)
    wdt.feed()
    while True:
        wdt.feed()
        if not is_collecting:
            key_scan(1)
        task_cnt += 1
        if task_cnt == 20:
            task_cnt = 1
            timer_1s_task()
        if change_warn_flag != 0:
            if change_warn_flag == 1:
                close_mpu_interrupt(1)
            elif change_warn_flag == 2:
                open_mpu_interrupt(1)
            change_warn_flag = 0
        if is_open_warn and not is_collecting:
            check_threshold()
        if warn_delay != 0:
            warn_delay -= 1
        if wifi_mode != 2 and not is_collecting and not vibrator.is_working:
            machine.lightsleep(50)
        else:
            time.sleep(0.05)

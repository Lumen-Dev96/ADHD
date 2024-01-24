import os


def check(sd):
    try:
        os.mount(sd, '/sd')  # 挂载SD卡
        dir_list = os.listdir('/sd')  # list directory contents
        if 'mpuData' not in dir_list:
            os.mkdir('/sd/mpuData')
        os.umount('/sd')  # 卸载SD卡
        print('sdCard is OK')
        return True
    except OSError:
        print("sdCard is error!")
        return False


def add_log(string):
    file = open('/sd/log.txt', 'a')
    file.write(string + '\r\n')
    file.close()


def write_config(config_str):
    file = None
    try:
        file = open('/sd/config', 'w')
        file.write(config_str)
        file.close()
        return True
    except OSError:
        if file is not None:
            file.close()
        try:
            return False
        except OSError:
            return False


def delete_all_file():
    file_list = os.listdir('/sd')  # list directory contents
    if len(file_list) > 0:
        for i in file_list:
            file_name = '/sd/' + i
            if file_name != '/sd/System Volume Information' and file_name != '/sd/readme.txt':
                print(file_name)
                os.remove(file_name)


def read_config():
    path_name = 'config'
    file = None
    config = 1
    try:
        file_list = os.listdir('/sd')  # list directory contents
        if path_name in file_list:
            file = open('/sd/' + path_name, 'r')
            config_str = file.read()
            config = int(config_str)
        else:
            file = open('/sd/' + path_name, 'w')
            file.write('1')
        file.close()
        sdcard_is_ok = True
    except OSError:
        if file is not None:
            file.close()
        sdcard_is_ok = False
        config = 1
    return config, sdcard_is_ok


# add_motion_analysis_data('MUP_00000001.txt', True)
def add_data_file(txt_name, is_include_gyro):
    file = None
    try:
        path_name = '/sd/mpuData/' + txt_name
        file = open(path_name, 'a')
        if is_include_gyro:
            file.write(' 采样时间 | 传感器1加速度（m/s^2） | 传感器2加速度（m/s^2） | 传感器1角速度（º/s） | 传感器2角速度（º/s）\r\n')
            file.write('mmdd_HHMMSS\tAx1\tAy1\tAz1\tAx2\tAy2\tAz2\tGx1\tGy1\tGz1\tGx2\tGy2\tGz2\r\n')
        else:
            file.write(' 采样时间 | 传感器1加速度（m/s^2） | 传感器2加速度（m/s^2）\r\n')
            file.write('mmdd_HHMMSS\tAx1\tAy1\tAz1\tAx2\tAy2\tAz2\r\n')
        file.close()
        sdcard_is_ok = True
    except OSError:
        sdcard_is_ok = False
        if file is not None:
            file.close()
    return sdcard_is_ok

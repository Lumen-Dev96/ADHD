import time
import machine


def update_local_time(date='2022-11-25-12-59-59'):
    date_list = date.split('-')
    date = (int(date_list[0]), int(date_list[1]), int(date_list[2]), 0, int(date_list[3]), int(date_list[4]), int(date_list[5]), 0)
    rtc = machine.RTC()
    rtc.datetime(date)
    print(time.localtime())


def get_format_date():
    my_time = time.localtime()
    my_time = '%04d%02d%02d_%02d%02d%02d' % (my_time[0], my_time[1], my_time[2], my_time[3], my_time[4], my_time[5])
    return my_time

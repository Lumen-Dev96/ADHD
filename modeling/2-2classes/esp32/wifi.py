import socket
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

while not wlan.isconnected():
    pass

addr = ('192.168.1.100', 12345)  # 请使用你的本地IP地址和端口
s = socket.socket()
s.connect(addr)

while True:
    data_to_send = "Hello from MicroPython Lumen!"
    s.send(data_to_send)
    time.sleep(1)
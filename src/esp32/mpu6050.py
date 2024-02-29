import time


class MPU6050:
    def __init__(self, iic, addr):
        self.iic = iic
        self.addr = addr
        self.init()

    def init(self):
        try:
            self.iic.writeto_mem(self.addr, 0x6B, b'\x80')
            time.sleep(0.1)
            self.iic.writeto_mem(self.addr, 0x6B, b'\x05')
            self.iic.writeto_mem(self.addr, 0x1B, b'\x18\x18')
            return True
        except OSError:
            print('\r\nSlave address:%d connection failed!' % self.addr)
            return False

    def set_mode(self, mode: str):
        try:
            if mode == 'sleep':
                self.iic.writeto_mem(self.addr, 0x6B, b'\x44')
            elif mode == 'cycle':
                self.iic.writeto_mem(self.addr, 0x6B, b'\x25\xc0')
            elif mode == 'normal':
                self.iic.writeto_mem(self.addr, 0x6B, b'\x05')
                self.iic.writeto_mem(self.addr, 0x1B, b'\x18\x18')
            else:
                print('TypeError:example(\'sleep\',\'cycle\',\'normal\')')
        except OSError:
            self.init()

    def get_data(self, include_gyro: bool):
        accelX = accelY = accelZ = gyroX = gyroY = gyroZ = 0
        try:
            if include_gyro:
                buffer = self.iic.readfrom_mem(self.addr, 59, 14)
                accelX = (buffer[0] << 8) | buffer[1]
                accelY = (buffer[2] << 8) | buffer[3]
                accelZ = (buffer[4] << 8) | buffer[5]
                gyroX = (buffer[8] << 8) | buffer[9]
                gyroY = (buffer[10] << 8) | buffer[11]
                gyroZ = (buffer[12] << 8) | buffer[13]

                # 换算陀螺仪
                if gyroX > 32767:
                    gyroX -= 65536
                gyroX = gyroX / 16.384

                if gyroY > 32767:
                    gyroY -= 65536
                gyroY = gyroY / 16.384

                if gyroZ > 32767:
                    gyroZ -= 65536
                gyroZ = gyroZ / 16.384
            else:
                buffer = self.iic.readfrom_mem(self.addr, 59, 6)
                accelX = (buffer[0] << 8) | buffer[1]
                accelY = (buffer[2] << 8) | buffer[3]
                accelZ = (buffer[4] << 8) | buffer[5]

            # 换算重力加速度
            if accelX > 32767:
                accelX -= 65536
            accelX = accelX * 1.225 / 256

            if accelY > 32767:
                accelY -= 65536
            accelY = accelY * 1.225 / 256

            if accelZ > 32767:
                accelZ -= 65536
            accelZ = accelZ * 1.225 / 256
        except OSError:
            pass
        return accelX, accelY, accelZ, gyroX, gyroY, gyroZ

    def open_INT(self, threshold):
        try:
            datas = bytes([threshold, 1])
            self.iic.writeto_mem(self.addr, 0x38, b'\x00')  # 先关闭MPU中断
            self.iic.writeto_mem(self.addr, 0x1F, datas)
            self.iic.writeto_mem(self.addr, 0x38, b'\x40')  # 再重新使能MPU中断
        except OSError:
            self.init()

    def close_INT(self):
        try:
            self.iic.writeto_mem(self.addr, 0x38, b'\x00')  # 关闭MPU中断
        except OSError:
            self.init()

    def get_INT_status(self):
        status = b'\x00'
        try:
            status = self.iic.readfrom_mem(self.addr, 0x3A, 1)
        except OSError:
            pass
        return status

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
        mpu_data = {'accelX': 0, 'accelY': 0, 'accelZ': 0, 'gyroX': 0, 'gyroY': 0, 'gyroZ': 0}
        try:
            if include_gyro:
                buffer = self.iic.readfrom_mem(self.addr, 59, 14)
                mpu_data['accelX'] = (buffer[0] << 8) | buffer[1]
                mpu_data['accelY'] = (buffer[2] << 8) | buffer[3]
                mpu_data['accelZ'] = (buffer[4] << 8) | buffer[5]
                mpu_data['gyroX'] = (buffer[8] << 8) | buffer[9]
                mpu_data['gyroY'] = (buffer[10] << 8) | buffer[11]
                mpu_data['gyroZ'] = (buffer[12] << 8) | buffer[13]

                # 换算陀螺仪
                if mpu_data['gyroX'] > 32767:
                    mpu_data['gyroX'] -= 65536
                mpu_data['gyroX'] = mpu_data['gyroX'] / 16.384

                if mpu_data['gyroY'] > 32767:
                    mpu_data['gyroY'] -= 65536
                mpu_data['gyroY'] = mpu_data['gyroY'] / 16.384

                if mpu_data['gyroZ'] > 32767:
                    mpu_data['gyroZ'] -= 65536
                mpu_data['gyroZ'] = mpu_data['gyroZ'] / 16.384
            else:
                buffer = self.iic.readfrom_mem(self.addr, 59, 6)
                mpu_data['accelX'] = (buffer[0] << 8) | buffer[1]
                mpu_data['accelY'] = (buffer[2] << 8) | buffer[3]
                mpu_data['accelZ'] = (buffer[4] << 8) | buffer[5]

            # 换算重力加速度
            if mpu_data['accelX'] > 32767:
                mpu_data['accelX'] -= 65536
            mpu_data['accelX'] = mpu_data['accelX'] * 1.225 / 256

            if mpu_data['accelY'] > 32767:
                mpu_data['accelY'] -= 65536
            mpu_data['accelY'] = mpu_data['accelY'] * 1.225 / 256

            if mpu_data['accelZ'] > 32767:
                mpu_data['accelZ'] -= 65536
            mpu_data['accelZ'] = mpu_data['accelZ'] * 1.225 / 256
        except OSError:
            pass
        return mpu_data

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

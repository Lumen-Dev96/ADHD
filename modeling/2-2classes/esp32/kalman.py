class KALMAN:
    Q = 0.00001  # 噪声的协方差，也可以理解为两个时刻之间噪声的偏差
    R = 0.01  # 状态的协方差，可以理解为两个时刻之间状态的偏差
    p_k_k1 = 1  # 上一时刻状态协方差
    kg = 0  # 卡尔曼增益
    p_k1_k1 = 1
    x_k_k1 = 0  # 上一时刻状态值
    kalman_adc_old = 0  # 上一次的卡尔曼滤波的到的最优估计值

    def __int__(self):
        self.Q = 0.00001  # 噪声的协方差，也可以理解为两个时刻之间噪声的偏差
        self.R = 0.01  # 状态的协方差，可以理解为两个时刻之间状态的偏差
        self.p_k_k1 = 1  # 上一时刻状态协方差
        self.kg = 0  # 卡尔曼增益
        self.p_k1_k1 = 1
        self.x_k_k1 = 0  # 上一时刻状态值
        self.kalman_adc_old = 0  # 上一次的卡尔曼滤波的到的最优估计值

    def get_A(self, adc_value):
        z_k = adc_value  # 测量值

        if abs(self.kalman_adc_old - adc_value) >= 20:  # 上一状态值与此刻测量值差距过大，进行简单的一阶滤波，0618黄金比例可以随意定哦
            x_k1_k1 = adc_value * 0.1 + self.kalman_adc_old * 0.9
        else:  # 差距不大直接使用
            x_k1_k1 = self.kalman_adc_old

        self.x_k_k1 = x_k1_k1  # 测量值
        self.p_k_k1 = self.p_k1_k1 + self.Q  # 公式二
        self.kg = self.p_k_k1 / (self.p_k_k1 + self.R)  # 公式三

        kalman_adc = self.x_k_k1 + self.kg * (z_k - self.kalman_adc_old)  # 计算最优估计值
        self.p_k1_k1 = (1 - self.kg) * self.p_k_k1  # 公式五
        self.p_k_k1 = self.p_k1_k1  # 更新状态协方差

        self.kalman_adc_old = kalman_adc
        return kalman_adc

    def get_G(self, adc_value):
        # global kalman_adc_old  # 定义两个全局变量，可以在程序中直接改变其中的值
        # global p_k1_k1, x_k_k1, adc_old_value, p_k_k1, kg
        z_k = adc_value  # 测量值

        if abs(self.kalman_adc_old - adc_value) >= 200:  # 上一状态值与此刻测量值差距过大，进行简单的一阶滤波，0618黄金比例可以随意定哦
            x_k1_k1 = adc_value * 0.1 + self.kalman_adc_old * 0.9
        else:  # 差距不大直接使用
            x_k1_k1 = self.kalman_adc_old

        self.x_k_k1 = x_k1_k1  # 测量值
        self.p_k_k1 = self.p_k1_k1 + self.Q  # 公式二
        self.kg = self.p_k_k1 / (self.p_k_k1 + self.R)  # 公式三

        kalman_adc = self.x_k_k1 + self.kg * (z_k - self.kalman_adc_old)  # 计算最优估计值
        self.p_k1_k1 = (1 - self.kg) * self.p_k_k1  # 公式五
        self.p_k_k1 = self.p_k1_k1  # 更新状态协方差

        self.kalman_adc_old = kalman_adc
        return kalman_adc

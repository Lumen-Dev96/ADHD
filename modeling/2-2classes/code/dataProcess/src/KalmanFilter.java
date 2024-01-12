public class KalmanFilter {
    private float Q ;  // 噪声的协方差，也可以理解为两个时刻之间噪声的偏差
    private float R;  // 状态的协方差，可以理解为两个时刻之间状态的偏差
    private float p_k_k1;  // 上一时刻状态协方差
    private float kg;  // 卡尔曼增益
    private float p_k1_k1;
    private float x_k_k1;  // 上一时刻状态值
    private float kalman_adc_old; // 上一次的卡尔曼滤波的到的最优估计值

    public KalmanFilter() {
        this.Q = 0.00001f;  // 噪声的协方差，也可以理解为两个时刻之间噪声的偏差
        this.R = 0.01f;  // 状态的协方差，可以理解为两个时刻之间状态的偏差
        this.p_k_k1 = 1;  // 上一时刻状态协方差
        this.kg = 0;  // 卡尔曼增益
        this.p_k1_k1 = 1;
        this.x_k_k1 = 0;  // 上一时刻状态值
        this.kalman_adc_old = 0; // 上一次的卡尔曼滤波的到的最优估计值
    }

    public float getAccel(float adc_value) {
        float z_k = adc_value;  // 测量值
        if (Math.abs(this.kalman_adc_old - adc_value) >= 20)  // 上一状态值与此刻测量值差距过大，进行简单的一阶滤波，0618黄金比例可以随意定哦
            this.x_k_k1 = adc_value * 0.1f + this.kalman_adc_old * 0.9f;
        else  // 差距不大直接使用
            this.x_k_k1 = this.kalman_adc_old;
        this.p_k_k1 = this.p_k1_k1 + this.Q;  // 公式二
        this.kg = this.p_k_k1 / (this.p_k_k1 + this.R); // 公式三

        float kalman_adc = this.x_k_k1 + this.kg * (z_k - this.kalman_adc_old);// 计算最优估计值
        this.p_k1_k1 = (1 - this.kg) * this.p_k_k1;// 公式五
        this.p_k_k1 = this.p_k1_k1;// 更新状态协方差

        this.kalman_adc_old = kalman_adc;
        return kalman_adc;
    }


    public float getGyro(float adc_value) {
        double z_k = adc_value;  // 测量值
        if (Math.abs(this.kalman_adc_old - adc_value) >= 200)  // 上一状态值与此刻测量值差距过大，进行简单的一阶滤波，0618黄金比例可以随意定哦
            this.x_k_k1 = (float) (adc_value * 0.1 + this.kalman_adc_old * 0.9);
        else  // 差距不大直接使用
            this.x_k_k1 = this.kalman_adc_old;
        this.p_k_k1 = this.p_k1_k1 + this.Q;  // 公式二
        this.kg = this.p_k_k1 / (this.p_k_k1 + this.R); // 公式三

        float kalman_adc = (float) (this.x_k_k1 + this.kg * (z_k - this.kalman_adc_old));// 计算最优估计值
        this.p_k1_k1 = (1 - this.kg) * this.p_k_k1;// 公式五
        this.p_k_k1 = this.p_k1_k1;// 更新状态协方差

        this.kalman_adc_old = kalman_adc;
        return kalman_adc;
    }
}

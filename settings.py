import os
import time
from pymycobot import *


# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 产品名称
CASES_DIR = {
    "1": "testcases/mercury",
    "2": "testcases/mercury_pro_gripper",
    "3": "testcases/mercury_my_hand",
    "4": "testcases/pro_gripper",
    "5": "testcases/my_hand",
    "6": "testcases/mycobot280",
    "7": "testcases/mycobot_320"
}

# 日志配置
LOG_CONFIG = {
    'name': 'elephant',
    'filename': os.path.join(BASE_DIR, r'log/log.log'),
    'debug': True,
    'mode': 'a',
    'encoding': 'utf-8'
}

REPORT_DIR = "allure-results"

# 水星x1七轴配置
class MercuryBase:
    # 机械臂运动数据
    speed = 50
    init_angles = [0, 0, 0, 0, 0, 90, 0]
    coords_init_angles = [0, 20, 0, -90, 0, 90, 0]

    # 七轴软件限位
    angles_min = [-165, -50, -165, -165, -165, -75, -165]
    angles_max = [165, 120, 165, 1, 165, 255, 165]
    ex_max_limit = [0,245,160]
    ex_min_limit = [-55,-70,-160]

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mercury.xlsx')
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mercury_pro_gripper.xlsx')
    MY_HAND_TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mercury_my_hand.xlsx')

    def __init__(self, left_port="/dev/left_arm", right_port="/dev/right_arm"):
        self.ml = Mercury(left_port,save_serial_log=1)
        self.mr = Mercury(right_port,save_serial_log=1,debug=1)

    def close(self):
        self.ml.close()
        self.mr.close()

    def go_zero(self):
        self.ml.send_angles(self.init_angles, self.speed)
        self.mr.send_angles(self.init_angles, self.speed)
        self.mr.send_angle(11,0,self.speed)
        self.mr.send_angle(12,0,self.speed)
        self.mr.send_angle(13,0,self.speed)

    def init_coords(self):
        self.ml.send_angles(self.coords_init_angles, self.speed)
        self.mr.send_angles(self.coords_init_angles, self.speed)

    def reset(self):
        self.mr.power_off()
        self.ml.power_off()
        self.ml.power_on()
        self.mr.power_on()

    def wait(self, timeout=30.0):
        """等待机械臂停止运动"""
        time.sleep(0.3)
        from common1 import logger

        start_time = time.time()
        last_log_time = start_time

        while self.ml.is_moving() or self.mr.is_moving():
            # 超时检查
            if time.time() - start_time > timeout:
                logger.error(f'机械臂运动超时（{timeout}秒）')
                raise TimeoutError(f'机械臂运动超时')

            # 每秒记录一次状态
            current_time = time.time()
            if current_time - last_log_time >= 1.0:
                elapsed = current_time - start_time
                left_status = "运动中" if self.ml.is_moving() else "已停止"
                right_status = "运动中" if self.mr.is_moving() else "已停止"
                logger.info(f'等待机械臂停止... 已等待{elapsed:.1f}秒 | 左臂:{left_status} | 右臂:{right_status}')
                last_log_time = current_time

            time.sleep(0.1)

        time.sleep(0.3)
        logger.info('机械臂运动完成')

    def power_on_only(self):
        self.mr.power_off()
        self.ml.power_off()
        self.ml.power_on_only()
        self.mr.power_on_only()

    def power_off(self):
        self.mr.power_off()
        self.ml.power_off()

    def set_default_torque_comp(self):
        torque_comp = [0,0,0,0,10,30,30]
        for i,c in enumerate(torque_comp):
            self.ml.set_torque_comp(i+1,c)
            self.mr.set_torque_comp(i+1,c)

    def set_default_pos_over_shoot(self):
        self.ml.set_pos_over_shoot(50)
        self.mr.set_pos_over_shoot(50)


    def set_default_p(self):
        for i in range(6):
            self.ml.set_hand_gripper_p(i + 1, 100)

    def set_default_d(self):
        for i in range(6):
            self.ml.set_hand_gripper_d(i + 1, 120)

    def set_default_i(self):
        for i in range(6):
            self.ml.set_hand_gripper_i(i + 1, 0)

    def set_default_cw(self):
        for i in range(6):
            self.ml.set_hand_gripper_clockwise(i + 1, 5)

    def set_default_cww(self):
        for i in range(6):
            self.ml.set_hand_gripper_counterclockwise(i + 1, 5)

    def set_default_mini_pressure(self):
        for i in range(6):
            self.ml.set_hand_gripper_min_pressure(i + 1, 0)

    def set_default_torque(self):
        for i in range(6):
            self.ml.set_hand_gripper_torque(i + 1, 100)

    def set_default_speed(self):
        for i in range(6):
            self.ml.set_hand_gripper_speed(i + 1, 100)

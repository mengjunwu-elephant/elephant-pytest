import os
import time

from pymycobot import *

from Myhand.MyHand import MyGripper_H100
from elegripper.elegripper import Gripper

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

# MyHand三指灵巧手配置
class MyHandBase:
    # 夹爪速度
    speed = 50

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/my_hand.xlsx')

    def __init__(self, port="com3", baudrate=115200):
        self.m = MyGripper_H100(port, baudrate=baudrate)

    def go_zero(self):
        self.m.set_gripper_angles([0, 0, 0, 0, 0, 0], self.speed)

    def set_default_p(self):
        for i in range(4):
            self.m.set_gripper_joint_P(i + 1, 100)
        self.m.set_gripper_joint_P(5,32)
        self.m.set_gripper_joint_P(6,32)

    def set_default_d(self):
        for i in range(6):
            self.m.set_gripper_joint_D(i + 1, 120)
        self.m.set_gripper_joint_D(5, 10)
        self.m.set_gripper_joint_D(6, 10)

    def set_default_i(self):
        for i in range(6):
            self.m.set_gripper_joint_I(i + 1, 0)

    def set_default_cw(self):
        for i in range(6):
            self.m.set_gripper_joint_cw(i + 1, 5)

    def set_default_cww(self):
        for i in range(6):
            self.m.set_gripper_joint_cww(i + 1, 5)

    def set_default_mini_pressure(self):
        for i in range(6):
            self.m.set_gripper_joint_mini_pressure(i + 1, 0)

    def set_default_torque(self):
        for i in range(6):
            self.m.set_gripper_joint_torque(i + 1, 100)

    def set_default_speed(self):
        for i in range(6):
            self.m.set_gripper_joint_speed(i + 1, 20)


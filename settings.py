import os
import time

from pymycobot import *

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

# Pro力控夹爪配置
class ProGripperBase:
    # 夹爪速度
    speed = 100
    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/pro_gripper.xlsx')

    def __init__(self, port="com5", baudrate=115200):
        self.m = Gripper(port, baudrate=baudrate)

    def go_zero(self):
        self.m.set_gripper_value(0, self.speed)


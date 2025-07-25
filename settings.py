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
# mycobot280配置
class Mycobot280Base:
    # 机械臂运动数据
    speed = 50
    coords_init_angles = [0,20,-90,-20,0,0]
    init_angles = [0, 0, 0, 0, 0, 0]
    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mycobot_280.xlsx')

    def __init__(self, port="com25", baudrate=115200):
        self.mc = MyCobot280(port, baudrate=baudrate)

    def default_settings(self):
        self.mc.power_on()
        self.mc.set_fresh_mode(0)
        self.mc.go_home()
        self.wait()
        self.mc.clear_error_information()

    def wait(self):
        time.sleep(0.5) # 等待机械臂开始运动
        while 1:
            if self.mc.is_moving() == 1:
                time.sleep(0.1)
            else:
                break
        time.sleep(0.5) # 等待机械臂停止运动

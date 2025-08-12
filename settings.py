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
    "7": "testcases/mycobot_320_123"
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

# mycobot320配置
class Mycobot320Base:
    # 机械臂运动数据
    speed = 50
    angles_init = [0, 0, -90, 0, 90, 0]
    zero_angles = [0, 0, 0, 0, 0, 0]
    zero_encodes = [2048, 2048, 2048, 2048, 2048, 2048]
    coords_init_angles = [0, 10, -100, 0, 90, 0]
    zero_coords = [190.2, -89.4, 235.9, 178.24, 0.18, -90.0]
    angles_init_coords = [-1.9, -154.2, 523.8, -89.99, 0.43, -177.29]

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mycobot_320.xlsx')

    def __init__(self, port="com26", baudrate=115200):
        self.m = MyCobot320(port, baudrate=baudrate)

    def range_comparison(self, expect_data, value, name='值'):
        value_max = expect_data[1]
        value_min = expect_data[0]
        if len(value) != 6:
            raise AssertionError(f"{name}长度不为6,实际为{len(value)}")
        elif all(value_min <= i <= value_max for i in value):
            return True
        else:
            raise AssertionError(f"{name}超出范围{value_min}~{value_max},实际值为{value}")

    def go_zero(self):
        self.m.send_angles(self.zero_angles, self.speed)
        time.sleep(0.5)
        while True:
            if self.m.is_moving() == 0:
                break
        time.sleep(1)

    def go_coords(self):
        self.m.send_angles(self.coords_init_angles, self.speed)
        time.sleep(0.5)
        while True:
            if self.m.is_moving() == 0:
                break
        time.sleep(1)

    def different_modes(self, ID):
        if ID <= 4:
            self.m.set_fresh_mode(0)
            if ID == 1:
                self.go_zero()
                self.m.send_angles(self.angles_init, self.speed)
            elif ID == 2:
                self.go_zero()
                self.m.send_angle(1, 100, self.speed)
            elif ID == 3:
                self.go_coords()
                self.m.send_coords(self.angles_init_coords, self.speed)
            elif ID == 4:
                self.go_coords()
                self.m.send_coord(1, self.zero_coords[0]+50, self.speed)
        else:
            self.m.set_fresh_mode(1)
            if ID == 5:
                self.go_zero()
                self.m.send_angles(self.angles_init, self.speed)
            elif ID == 6:
                self.go_zero()
                self.m.send_angle(1, 100, self.speed)
            elif ID == 7:
                self.go_coords()
                self.m.send_coords(self.angles_init_coords, self.speed)
            elif ID == 8:
                self.go_coords()
                self.m.send_coord(1, self.zero_coords[0]+50, self.speed)

    def wait(self):
        time.sleep(0.5)  # 等待机械臂开始运动
        while 1:
            if self.m.is_moving() == 1:
                time.sleep(0.1)
            else:
                break
        time.sleep(0.5)

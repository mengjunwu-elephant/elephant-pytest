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
    "6": "testcases/mycobot_280",
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
    coords_init_angles = [0,20,-90,-20,0,0] #坐标值：[128.8, -62.2, 227.7, 178.42, -0.28, -90.08]
    init_angles = [0, 0, 0, 0, 0, 0]

    angles_min = [-168, -135, -150, -145, -155, -180]
    angles_max = [168, 135, 150, 145, 160, 180]

    # 自适应夹爪配置
    hts_gripper_torque = 200
    hts_gripper_protect_current = 300

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mycobot_280.xlsx')

    def __init__(self, port="com5", baudrate=115200):
        self.mc = MyCobot280(port, baudrate=baudrate,debug=1)

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
        time.sleep(1) # 等待机械臂停止运动

    def default_angles(self):
        for i,j in enumerate(self.angles_min):
            self.mc.set_joint_min(i+1,j)
            time.sleep(0.1)
        for i,j in enumerate(self.angles_max):
            self.mc.set_joint_max(i+1,j)
            time.sleep(0.1)
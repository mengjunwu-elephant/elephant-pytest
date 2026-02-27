import os
import time
from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 产品名称
CASES_DIR = {
    "1": "testcases/mercury_e1",
    "2": "testcases/mercury_e1_pro_gripper"
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

# MercuryE1配置
class MercuryE1Base:
    # 机械臂运动数据
    speed = 50
    coords_init_angles = [0, -10, 0, -90, 0, -90, 0] #坐标值：[212.6, -0.1, 418.1, -179.99, 9.99, 179.96]
    zero_angles = [0, 0, 0, 0, 0, 0, 0]
    min_angles = [-155,-55,-160,-135,-160,-100,-135]
    max_angles = [155,105,160,18,160,117,135]

    # collision_threshold = [100, 100, 100, 100, 100, 100]
    # torque_comp = [0, 0, 0, 10, 30, 30]
    # fusion_parameters = [150,1000,100,4000]

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mercury_e1.xlsx')
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/pro_gripper.xlsx')

    def __init__(self, port='com3'):
        self.mc = MercuryE1(port=port,debug=True)

    def default_settings(self):
        self.mc.set_fresh_mode(0)
        self.mc.set_debug_state(0)
        self.mc.set_movement_type(1)

    def default_speed(self):
        self.mc.set_max_speed(0, 150)
        self.mc.set_max_speed(1, 200)
        self.mc.set_max_acc(0, 200)
        self.mc.set_max_acc(1, 400)

    def default_angle(self):
        for i,j in enumerate(self.min_angles):
            self.mc.set_joint_min_angle(i+1,j)
            time.sleep(0.1)
        for i,j in enumerate(self.max_angles):
            self.mc.set_joint_max_angle(i+1,j)
            time.sleep(0.1)

    def default_base_io_output(self):
        for i in range(12):
            self.mc.set_base_io_output(i+1,0)
            time.sleep(0.2)

    def default_digital_io_output(self):
        for i in range(2):
            self.mc.set_digital_output(i+1,0)
            time.sleep(0.2)

    def default_tool_reference(self):
        self.mc.set_tool_reference([0,0,0,0,0,0])
        self.mc.set_end_type(0)

    def default_world_reference(self):
        self.mc.set_world_reference([0,0,0,0,0,0])
        self.mc.set_reference_frame(0)

    def default_collision_threshold(self):
        for i,j in enumerate(self.collision_threshold):
            self.mc.set_collision_threshold(i+1,j)

    def default_torque_comp(self):
        for i,j in enumerate(self.torque_comp):
            self.mc.set_torque_comp(i+1,0,j)

    def default_filter_len(self):
        self.mc.set_filter_len(5,60)

    def default_fusion_parameters(self):
        for i,j in enumerate(self.fusion_parameters):
            self.mc.set_fusion_parameters(i+1,j)

    def go_zero(self):
        self.mc.send_angles(self.zero_angles, self.speed)
        time.sleep(2)

    def wait(self):
        time.sleep(0.3)
        while self.mc.is_moving():
            time.sleep(0.1)
        time.sleep(1)
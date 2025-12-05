import os
import time
from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 产品名称
CASES_DIR = {
    "1": "testcases/UltraArm_P1",
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

# UltraArm P1配置
class UltraArmP1Base:
    # 机械臂运动数据
    speed = 50
    zero_angles = [0, 0, 0, 0, 0, 0]
    min_angles = [-162,-114,-154,-162,-162,-165]
    max_angles = [162,114,154,162,162,165]

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/UltraArm_P1.xlsx')

    def __init__(self):
        self.mc = UltraArmP1()

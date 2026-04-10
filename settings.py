import os
import time
from typing import Optional

from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 产品名称
CASES_DIR = {
    "1": "testcases/MyAGVPro",
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

# MyAGVPro配置
class MyAGVProBase:

    speed = 0.5

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/MyAGVPro.xlsx')

    def __init__(self, DEFAULT_PORT="/dev/agvpro_controller"):
        self.mc = MyAGVPro(port=DEFAULT_PORT)

    def reset(self):
        self.mc.power_off()
        self.mc.power_on()

    def set_motor_enable_reset(self):
        self.mc.set_motor_enable(254, 1)

    def set_led_color_reset(self):
        self.mc.set_led_mode(1)
        self.mc.set_led_color(0, (0, 255, 0), 85)
        self.mc.set_led_color(1, (0, 255, 0), 85)
        self.mc.set_led_mode(0)


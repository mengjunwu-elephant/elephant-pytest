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

    # 默认控制器 port（无环境变量时使用）
    DEFAULT_PORT = "/dev/agvpro_controller"
    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/MyAGVPro.xlsx')

    def __init__(self, DEFAULT_PORT):
        self.mc = MyAGVPro(port=DEFAULT_PORT)


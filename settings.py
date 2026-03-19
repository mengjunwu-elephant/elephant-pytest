import os
import time
from typing import Optional

from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 默认控制器 IP（无环境变量时使用）
DEFAULT_MYCOBOT450_IP = "192.168.0.232"


def resolve_mycobot450_ip(explicit: Optional[str] = None) -> str:
    """解析机械臂 IP：显式参数 > 环境变量 MYCOBOT450_IP / Mycobot450_IP > 默认常量。"""
    if explicit is not None and str(explicit).strip() != "":
        return str(explicit).strip()
    return (
        os.environ.get("MYCOBOT450_IP", "").strip()
        or os.environ.get("Mycobot450_IP", "").strip()
        or DEFAULT_MYCOBOT450_IP
    )


def _client_debug_from_env() -> bool:
    """未设置 MYCOBOT450_DEBUG 时默认 True，与历史 Pro450Client(debug=True) 行为一致。"""
    v = os.environ.get("MYCOBOT450_DEBUG", "").strip().lower()
    if v in ("0", "false", "no"):
        return False
    if v in ("1", "true", "yes"):
        return True
    return True


def _move_wait_timeout_sec() -> float:
    raw = os.environ.get("MYCOBOT450_MOVE_TIMEOUT_SEC", "").strip()
    if not raw:
        return 120.0
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 120.0

# 产品名称
CASES_DIR = {
    "1": "testcases/mycobot_450",
    "2": "testcases/mycobot450_pro_gripper"
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

# mycobot450配置
class Mycobot450Base:
    # 机械臂运动数据
    speed = 50
    coords_init_angles =[0, 30, -100, -20, 0.0, 0.0] #坐标值：[149.9, -86.8, 298.4, 179.99, 0.0, -90.0]
    zero_angles = [0, 0, 0, 0, 0, 0]
    min_angles = [-162,-125,-154,-162,-162,-165]
    max_angles = [162,125,154,162,162,165]

    collision_threshold = [100, 100, 100, 100, 100, 100]
    torque_comp = [0, 0, 0, 10, 30, 30]
    fusion_parameters = [150,1000,100,4000]

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/mycobot_450.xlsx')
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(BASE_DIR, r'test_data/pro_gripper.xlsx')

    # is_moving 轮询最大等待（秒），可通过环境变量 MYCOBOT450_MOVE_TIMEOUT_SEC 覆盖
    move_wait_timeout_sec: float = _move_wait_timeout_sec()

    def __init__(self, ip: Optional[str] = None) -> None:
        resolved = resolve_mycobot450_ip(ip)
        self.mc = Pro450Client(ip=resolved, debug=_client_debug_from_env())

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

    def wait(self) -> None:
        """等待运动结束；带超时，避免 is_moving 异常时死等。"""
        deadline = time.monotonic() + float(self.move_wait_timeout_sec)
        time.sleep(0.3)
        while self.mc.is_moving():
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"wait() 超时：{self.move_wait_timeout_sec}s 内 is_moving 仍为真"
                )
            time.sleep(0.1)
        time.sleep(1)
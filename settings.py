# -*- coding: utf-8 -*-
"""多产品线共享配置（main 分支融合各机械臂分支的 settings）。"""
from __future__ import annotations

import os
import time
from typing import Optional, Union

from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# MyCobot Pro 450（网络）
# ---------------------------------------------------------------------------
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
    v = os.environ.get("MYCOBOT450_DEBUG", "").strip().lower()
    if v in ("0", "false", "no"):
        return False
    if v in ("1", "true", "yes"):
        return True
    return True


def _mycobot450_move_wait_timeout_sec() -> float:
    raw = os.environ.get("MYCOBOT450_MOVE_TIMEOUT_SEC", "").strip()
    if not raw:
        return 120.0
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 120.0


# ---------------------------------------------------------------------------
# UltraArm P1（串口）
# ---------------------------------------------------------------------------
DEFAULT_ULTRAARM_PORT = "com5"
DEFAULT_ULTRAARM_BAUD = 1000000


def resolve_ultraarm_port(explicit: Optional[str] = None) -> str:
    if explicit is not None and str(explicit).strip() != "":
        return str(explicit).strip()
    return os.environ.get("ULTRAARM_PORT", "").strip() or DEFAULT_ULTRAARM_PORT


def resolve_ultraarm_baud(explicit: Optional[Union[int, str]] = None) -> int:
    if explicit is not None and str(explicit).strip() != "":
        try:
            return int(explicit)
        except (TypeError, ValueError):
            return DEFAULT_ULTRAARM_BAUD
    raw = os.environ.get("ULTRAARM_BAUD", "").strip()
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            pass
    return DEFAULT_ULTRAARM_BAUD


def _ultraarm_debug_from_env() -> int:
    v = os.environ.get("ULTRAARM_DEBUG", "").strip().lower()
    if v in ("0", "false", "no"):
        return 0
    if v in ("1", "true", "yes"):
        return 1
    return 1


def _ultraarm_move_wait_timeout_sec() -> float:
    raw = os.environ.get("ULTRAARM_MOVE_TIMEOUT_SEC", "").strip()
    if not raw:
        return 120.0
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 120.0


# ---------------------------------------------------------------------------
# 兼容 main.py 数字菜单：按仓库内实际存在的用例根路径（旧脚本仍可用）
# ---------------------------------------------------------------------------
CASES_DIR = {
    "1": "testcases/mycobot_450",
    "2": "testcases/mycobot450_pro_gripper",
    "3": "testcases/mycobot_280",
    "4": "testcases/mercury",
    "5": "testcases/mercury_pro_gripper",
    "6": "testcases/mercury_my_hand",
    "7": "testcases/mercury_e1",
    "8": "testcases/mercury_e1_pro_gripper",
    "9": "testcases/UltraArm_P1",
    "10": "testcases/UltraArm_P1_Attachments",
}

LOG_CONFIG = {
    "name": "elephant",
    "filename": os.path.join(BASE_DIR, r"log/log.log"),
    "debug": True,
    "mode": "a",
    "encoding": "utf-8",
}

REPORT_DIR = "allure-results"


# ---------------------------------------------------------------------------
# MyCobot Pro 450
# ---------------------------------------------------------------------------
class Mycobot450Base:
    speed = 50
    coords_init_angles = [0, 30, -100, -20, 0.0, 0.0]
    zero_angles = [0, 0, 0, 0, 0, 0]
    min_angles = [-162, -125, -154, -162, -162, -165]
    max_angles = [162, 125, 154, 162, 162, 165]

    collision_threshold = [100, 100, 100, 100, 100, 100]
    torque_comp = [0, 0, 0, 10, 30, 30]
    fusion_parameters = [150, 1000, 100, 4000]

    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mycobot_450.xlsx")
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/pro_gripper.xlsx")

    move_wait_timeout_sec: float = _mycobot450_move_wait_timeout_sec()

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
        for i, j in enumerate(self.min_angles):
            self.mc.set_joint_min_angle(i + 1, j)
            time.sleep(0.1)
        for i, j in enumerate(self.max_angles):
            self.mc.set_joint_max_angle(i + 1, j)
            time.sleep(0.1)

    def default_base_io_output(self):
        for i in range(12):
            self.mc.set_base_io_output(i + 1, 0)
            time.sleep(0.2)

    def default_digital_io_output(self):
        for i in range(2):
            self.mc.set_digital_output(i + 1, 0)
            time.sleep(0.2)

    def default_tool_reference(self):
        self.mc.set_tool_reference([0, 0, 0, 0, 0, 0])
        self.mc.set_end_type(0)

    def default_world_reference(self):
        self.mc.set_world_reference([0, 0, 0, 0, 0, 0])
        self.mc.set_reference_frame(0)

    def default_collision_threshold(self):
        for i, j in enumerate(self.collision_threshold):
            self.mc.set_collision_threshold(i + 1, j)

    def default_torque_comp(self):
        for i, j in enumerate(self.torque_comp):
            self.mc.set_torque_comp(i + 1, 0, j)

    def default_filter_len(self):
        self.mc.set_filter_len(5, 60)

    def default_fusion_parameters(self):
        for i, j in enumerate(self.fusion_parameters):
            self.mc.set_fusion_parameters(i + 1, j)

    def go_zero(self):
        self.mc.send_angles(self.zero_angles, self.speed)
        time.sleep(2)

    def wait(self) -> None:
        deadline = time.monotonic() + float(self.move_wait_timeout_sec)
        time.sleep(0.3)
        while self.mc.is_moving():
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"wait() 超时：{self.move_wait_timeout_sec}s 内 is_moving 仍为真"
                )
            time.sleep(0.1)
        time.sleep(1)


# ---------------------------------------------------------------------------
# Mercury X1 七轴双臂（mercury_x1 分支）
# ---------------------------------------------------------------------------
class MercuryBase:
    speed = 50
    init_angles = [0, 0, 0, 0, 0, 90, 0]
    coords_init_angles = [0, 20, 0, -90, 0, 90, 0]

    angles_min = [-165, -50, -165, -165, -165, -75, -165]
    angles_max = [165, 120, 165, 1, 165, 255, 165]
    ex_max_limit = [0, 245, 160]
    ex_min_limit = [-55, -70, -160]

    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mercury.xlsx")
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(
        BASE_DIR, r"test_data/mercury_pro_gripper.xlsx"
    )
    MY_HAND_TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mercury_my_hand.xlsx")

    def __init__(self, left_port="/dev/left_arm", right_port="/dev/right_arm"):
        self.ml = Mercury(left_port, save_serial_log=1)
        self.mr = Mercury(right_port, save_serial_log=1, debug=1)

    def close(self):
        self.ml.close()
        self.mr.close()

    def go_zero(self):
        self.ml.send_angles(self.init_angles, self.speed)
        self.mr.send_angles(self.init_angles, self.speed)
        self.mr.send_angle(11, 0, self.speed)
        self.mr.send_angle(12, 0, self.speed)
        self.mr.send_angle(13, 0, self.speed)

    def init_coords(self):
        self.ml.send_angles(self.coords_init_angles, self.speed)
        self.mr.send_angles(self.coords_init_angles, self.speed)

    def reset(self):
        self.mr.power_off()
        self.ml.power_off()
        self.ml.power_on()
        self.mr.power_on()

    def wait(self, timeout=30.0):
        """等待机械臂停止运动（带超时）。"""
        time.sleep(0.3)
        from common1 import logger

        start_time = time.time()
        last_log_time = start_time
        logger.info(
            f"当前左臂运动状态为{self.ml.is_moving()}，当前右臂运动状态为{self.mr.is_moving()}"
        )
        while self.ml.is_moving() or self.mr.is_moving():
            if time.time() - start_time > timeout:
                logger.error(f"机械臂运动超时（{timeout}秒）")
                raise TimeoutError("机械臂运动超时")
            current_time = time.time()
            if current_time - last_log_time >= 1.0:
                elapsed = current_time - start_time
                left_status = "运动中" if self.ml.is_moving() else "已停止"
                right_status = "运动中" if self.mr.is_moving() else "已停止"
                logger.info(
                    f"等待机械臂停止... 已等待{elapsed:.1f}秒 | 左臂:{left_status} | 右臂:{right_status}"
                )
                last_log_time = current_time

        time.sleep(0.3)
        logger.info("机械臂运动完成")

    def power_on_only(self):
        self.mr.power_off()
        self.ml.power_off()
        self.ml.power_on_only()
        self.mr.power_on_only()

    def power_off(self):
        self.mr.power_off()
        self.ml.power_off()

    def set_default_torque_comp(self):
        torque_comp = [0, 0, 0, 0, 10, 30, 30]
        for i, c in enumerate(torque_comp):
            self.ml.set_torque_comp(i + 1, c)
            self.mr.set_torque_comp(i + 1, c)

    def set_default_pos_over_shoot(self):
        self.ml.set_pos_over_shoot(50)
        self.mr.set_pos_over_shoot(50)

    def set_default_joint_min_angle(self):
        for i in range(6):
            self.ml.set_joint_min_angle(i + 1, self.angles_min[i])
            self.mr.set_joint_min_angle(i + 1, self.angles_min[i])

    def set_default_joint_max_angle(self):
        for i in range(6):
            self.ml.set_joint_max_angle(i + 1, self.angles_max[i])
            self.mr.set_joint_max_angle(i + 1, self.angles_max[i])

    def set_default_p(self):
        for i in range(6):
            self.ml.set_hand_gripper_p(i + 1, 100)

    def set_default_d(self):
        for i in range(6):
            self.ml.set_hand_gripper_d(i + 1, 120)

    def set_default_i(self):
        for i in range(6):
            self.ml.set_hand_gripper_i(i + 1, 0)

    def set_default_cw(self):
        for i in range(6):
            self.ml.set_hand_gripper_clockwise(i + 1, 5)

    def set_default_cww(self):
        for i in range(6):
            self.ml.set_hand_gripper_counterclockwise(i + 1, 5)

    def set_default_mini_pressure(self):
        for i in range(6):
            self.ml.set_hand_gripper_min_pressure(i + 1, 0)

    def set_default_torque(self):
        for i in range(6):
            self.ml.set_hand_gripper_torque(i + 1, 100)

    def set_default_speed(self):
        for i in range(6):
            self.ml.set_hand_gripper_speed(i + 1, 100)


# ---------------------------------------------------------------------------
# MyCobot 280
# ---------------------------------------------------------------------------
class Mycobot280Base:
    speed = 50
    coords_init_angles = [0, 20, -90, -20, 0, 0]
    init_angles = [0, 0, 0, 0, 0, 0]

    angles_min = [-168, -135, -150, -145, -155, -180]
    angles_max = [168, 135, 150, 145, 160, 180]

    hts_gripper_torque = 200
    hts_gripper_protect_current = 300

    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mycobot_280.xlsx")

    def __init__(self, port="com5", baudrate=115200):
        self.mc = MyCobot280(port, baudrate=baudrate, debug=1)

    def default_settings(self):
        self.mc.power_on()
        self.mc.set_fresh_mode(0)
        self.mc.go_home()
        self.wait()
        self.mc.clear_error_information()

    def wait(self):
        time.sleep(0.5)
        while True:
            if self.mc.is_moving() == 1:
                time.sleep(0.1)
            else:
                break
        time.sleep(1)

    def default_angles(self):
        for i, j in enumerate(self.angles_min):
            self.mc.set_joint_min(i + 1, j)
            time.sleep(0.1)
        for i, j in enumerate(self.angles_max):
            self.mc.set_joint_max(i + 1, j)
            time.sleep(0.1)


# ---------------------------------------------------------------------------
# UltraArm P1
# ---------------------------------------------------------------------------
class UltraArmP1Base:
    speed = 5000
    zero_angles = [0, 0, 90, 0]
    coords_init_angles = [0, 0, 110, 0]
    min_angles = [-162, -114, -154, -162, -162, -165]
    max_angles = [162, 114, 154, 162, 162, 165]

    base_io_pin_count = 12

    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/UltraArm_P1.xlsx")
    ATTACHMENTS_TEST_DATA_FILE = os.path.join(
        BASE_DIR, r"test_data/UltraArm_P1_Attachments.xlsx"
    )

    move_wait_timeout_sec: float = _ultraarm_move_wait_timeout_sec()

    def __init__(
        self,
        port: Optional[str] = None,
        baud: Optional[Union[int, str]] = None,
        debug: Optional[int] = None,
    ) -> None:
        resolved_port = resolve_ultraarm_port(port)
        resolved_baud = resolve_ultraarm_baud(baud)
        dbg = _ultraarm_debug_from_env() if debug is None else int(debug)
        self.mc = UltraArmP1(resolved_port, resolved_baud, debug=dbg)

    def default_base_io_output(self) -> None:
        for i in range(1, int(self.base_io_pin_count) + 1):
            self.mc.set_base_io_output(i, 0)
            time.sleep(0.2)

    def go_zero(self) -> None:
        self.mc.set_angles(self.zero_angles, self.speed)
        self.wait()

    def wait(self) -> None:
        deadline = time.monotonic() + float(self.move_wait_timeout_sec)
        time.sleep(0.3)
        while self.mc.get_run_status():
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"wait() 超时：{self.move_wait_timeout_sec}s 内 get_run_status 仍为真"
                )
            time.sleep(0.1)
        time.sleep(0.3)


# ---------------------------------------------------------------------------
# Mercury E1（七轴单臂，与 Pro450 接口风格接近）
# ---------------------------------------------------------------------------
class MercuryE1Base:
    speed = 50
    coords_init_angles = [0, -10, 0, -90, 0, -90, 0]
    zero_angles = [0, 0, 0, 0, 0, 0, 0]
    min_angles = [-155, -55, -160, -135, -160, -100, -135]
    max_angles = [155, 105, 160, 18, 160, 117, 135]

    collision_threshold = [100, 100, 100, 100, 100, 100, 100]
    torque_comp = [0, 0, 0, 10, 30, 30, 30]
    fusion_parameters = [150, 1000, 100, 4000]

    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mercury_e1.xlsx")
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/pro_gripper.xlsx")

    def __init__(self, port="com3"):
        self.mc = MercuryE1(port=port, debug=True)

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
        for i, j in enumerate(self.min_angles):
            self.mc.set_joint_min_angle(i + 1, j)
            time.sleep(0.1)
        for i, j in enumerate(self.max_angles):
            self.mc.set_joint_max_angle(i + 1, j)
            time.sleep(0.1)

    def default_base_io_output(self):
        for i in range(12):
            self.mc.set_base_io_output(i + 1, 0)
            time.sleep(0.2)

    def default_digital_io_output(self):
        for i in range(2):
            self.mc.set_digital_output(i + 1, 0)
            time.sleep(0.2)

    def default_tool_reference(self):
        self.mc.set_tool_reference([0, 0, 0, 0, 0, 0])
        self.mc.set_end_type(0)

    def default_world_reference(self):
        self.mc.set_world_reference([0, 0, 0, 0, 0, 0])
        self.mc.set_reference_frame(0)

    def default_collision_threshold(self):
        for i, j in enumerate(self.collision_threshold):
            self.mc.set_collision_threshold(i + 1, j)

    def default_torque_comp(self):
        for i, j in enumerate(self.torque_comp):
            self.mc.set_torque_comp(i + 1, 0, j)

    def default_filter_len(self):
        self.mc.set_filter_len(5, 60)

    def default_fusion_parameters(self):
        for i, j in enumerate(self.fusion_parameters):
            self.mc.set_fusion_parameters(i + 1, j)

    def go_zero(self):
        self.mc.send_angles(self.zero_angles, self.speed)
        time.sleep(2)

    def wait(self):
        time.sleep(0.3)
        while self.mc.is_moving():
            time.sleep(0.1)
        time.sleep(1)

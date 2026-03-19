import os
import time
from typing import Optional

from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 默认串口（无环境变量时）；Windows 可设为 COM3 等
DEFAULT_MERCURY_PORT = "/dev/ttyAMA1"
DEFAULT_MERCURY_SAVE_SERIAL_LOG = 1


def resolve_mercury_port(explicit: Optional[str] = None) -> str:
    """单臂串口：显式参数 > MERCURY_PORT / MERCURY_LEFT_PORT（兼容旧名）> 默认。"""
    if explicit is not None and str(explicit).strip() != "":
        return str(explicit).strip()
    return (
        os.environ.get("MERCURY_PORT", "").strip()
        or os.environ.get("MERCURY_LEFT_PORT", "").strip()
        or DEFAULT_MERCURY_PORT
    )


# 兼容历史调用名
resolve_mercury_left_port = resolve_mercury_port


def _mercury_save_serial_log_from_env() -> int:
    raw = os.environ.get("MERCURY_SAVE_SERIAL_LOG", "").strip()
    if raw == "":
        return DEFAULT_MERCURY_SAVE_SERIAL_LOG
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_MERCURY_SAVE_SERIAL_LOG


def _mercury_move_wait_timeout_sec() -> float:
    raw = os.environ.get("MERCURY_MOVE_TIMEOUT_SEC", "").strip()
    if not raw:
        return 120.0
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 120.0


# 产品名称
CASES_DIR = {
    "1": "testcases/mercury",
    "2": "testcases/mercury_pro_gripper",
    "3": "testcases/mercury_my_hand",
    "4": "testcases/pro_gripper",
    "5": "testcases/my_hand",
    "6": "testcases/mycobot280",
    "7": "testcases/mycobot_320",
}

# 日志配置
LOG_CONFIG = {
    "name": "elephant",
    "filename": os.path.join(BASE_DIR, r"log/log.log"),
    "debug": True,
    "mode": "a",
    "encoding": "utf-8",
}

REPORT_DIR = "allure-results"


# 水星 A1 七轴（单臂），pymycobot 实例为 mc
class MercuryBase:
    # 机械臂运动数据
    speed = 50
    init_angles = [0, 0, 0, 0, 0, 90, 0]
    coords_init_angles = [0, 20, 0, -90, 0, 90, 0]

    # 七轴软件限位
    angles_min = [-165, -50, -165, -165, -165, -75, -165]
    angles_max = [165, 120, 165, 1, 165, 255, 165]
    ex_max_limit = [0, 245, 160]
    ex_min_limit = [-55, -70, -160]

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mercury.xlsx")
    PRO_GRIPPER_TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mercury_pro_gripper.xlsx")
    MY_HAND_TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/mercury_my_hand.xlsx")

    move_wait_timeout_sec: float = _mercury_move_wait_timeout_sec()

    def __init__(
        self,
        left_port: Optional[str] = None,
        save_serial_log: Optional[int] = None,
        port: Optional[str] = None,
    ) -> None:
        """left_port 与 port 二选一，均表示单臂串口；left_port 仅保留兼容旧代码。"""
        serial_port = resolve_mercury_port(port if port is not None else left_port)
        slog = (
            _mercury_save_serial_log_from_env()
            if save_serial_log is None
            else int(save_serial_log)
        )
        self.mc = Mercury(serial_port, save_serial_log=slog)

    def close(self) -> None:
        self.mc.close()

    def go_zero(self) -> None:
        self.mc.send_angles(self.init_angles, self.speed)

    def init_coords(self) -> None:
        self.mc.send_angles(self.coords_init_angles, self.speed)

    def reset(self) -> None:
        self.mc.power_off()
        self.mc.power_on()

    def wait(self, timeout: Optional[float] = None) -> None:
        """等待机械臂停止运动；默认超时由 MERCURY_MOVE_TIMEOUT_SEC / move_wait_timeout_sec 控制。"""
        from common1 import logger

        limit = float(timeout if timeout is not None else self.move_wait_timeout_sec)
        time.sleep(0.3)
        start = time.monotonic()
        deadline = start + limit
        last_log_time = start
        logger.info(f"当前运动状态为{self.mc.is_moving()}")
        while self.mc.is_moving():
            now = time.monotonic()
            if now > deadline:
                logger.error(f"机械臂运动超时（{limit}秒）")
                raise TimeoutError("机械臂运动超时")
            if now - last_log_time >= 1.0:
                elapsed = now - start
                status = "运动中" if self.mc.is_moving() else "已停止"
                logger.info(f"等待机械臂停止... 已等待{elapsed:.1f}秒 | {status}")
                last_log_time = now
            time.sleep(0.05)

        time.sleep(0.3)
        logger.info("机械臂运动完成")

    def power_on_only(self) -> None:
        self.mc.power_off()
        self.mc.power_on_only()

    def power_off(self) -> None:
        self.mc.power_off()

    def set_default_torque_comp(self) -> None:
        torque_comp = [0, 0, 0, 0, 10, 30, 30]
        for i, c in enumerate(torque_comp):
            self.mc.set_torque_comp(i + 1, c)

    def set_default_pos_over_shoot(self) -> None:
        self.mc.set_pos_over_shoot(50)

    def set_default_joint_min_angle(self) -> None:
        for i in range(6):
            self.mc.set_joint_min_angle(i + 1, self.angles_min[i])

    def set_default_joint_max_angle(self) -> None:
        for i in range(6):
            self.mc.set_joint_max_angle(i + 1, self.angles_max[i])

    # 三指默认参数
    def set_default_p(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_p(i + 1, 100)

    def set_default_d(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_d(i + 1, 120)

    def set_default_i(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_i(i + 1, 0)

    def set_default_cw(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_clockwise(i + 1, 5)

    def set_default_cww(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_counterclockwise(i + 1, 5)

    def set_default_mini_pressure(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_min_pressure(i + 1, 0)

    def set_default_torque(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_torque(i + 1, 100)

    def set_default_speed(self) -> None:
        for i in range(6):
            self.mc.set_hand_gripper_speed(i + 1, 100)

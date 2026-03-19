import os
import time
from typing import Optional, Union

from pymycobot import *

# 项目路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 默认串口参数（无环境变量时使用）
DEFAULT_ULTRAARM_PORT = "com4"
DEFAULT_ULTRAARM_BAUD = 115200


def resolve_ultraarm_port(explicit: Optional[str] = None) -> str:
    """串口名：显式参数 > 环境变量 ULTRAARM_PORT > 默认常量。"""
    if explicit is not None and str(explicit).strip() != "":
        return str(explicit).strip()
    return os.environ.get("ULTRAARM_PORT", "").strip() or DEFAULT_ULTRAARM_PORT


def resolve_ultraarm_baud(explicit: Optional[Union[int, str]] = None) -> int:
    """波特率：显式参数 > 环境变量 ULTRAARM_BAUD > 默认常量。"""
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
    """未设置 ULTRAARM_DEBUG 时默认 1，与历史 UltraArmP1(..., debug=1) 一致。"""
    v = os.environ.get("ULTRAARM_DEBUG", "").strip().lower()
    if v in ("0", "false", "no"):
        return 0
    if v in ("1", "true", "yes"):
        return 1
    return 1


def _move_wait_timeout_sec() -> float:
    raw = os.environ.get("ULTRAARM_MOVE_TIMEOUT_SEC", "").strip()
    if not raw:
        return 120.0
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 120.0


# 产品名称
CASES_DIR = {
    "1": "testcases/UltraArm_P1",
    "2": "testcases/UltraArm_P1_Attachments",
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


# UltraArm_P1 配置
class UltraArmP1Base:
    # 机械臂运动数据
    speed = 5000
    zero_angles = [0, 0, 90, 0]
    coords_init_angles = [0, 0, 110, 0]
    min_angles = [-162, -114, -154, -162, -162, -165]
    max_angles = [162, 114, 154, 162, 162, 165]

    # 底座 IO 复位时遍历的引脚数量（按实际硬件修改）
    base_io_pin_count = 12

    # 测试数据配置
    TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/UltraArm_P1.xlsx")
    ATTACHMENTS_TEST_DATA_FILE = os.path.join(BASE_DIR, r"test_data/UltraArm_P1_Attachments.xlsx")

    move_wait_timeout_sec: float = _move_wait_timeout_sec()

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
        """底座 IO 输出全部置低（与 mycobot_450 框架中同名方法语义对齐）。"""
        for i in range(1, int(self.base_io_pin_count) + 1):
            self.mc.set_base_io_output(i, 0)
            time.sleep(0.2)

    def go_zero(self) -> None:
        self.mc.set_angles(self.zero_angles, self.speed)
        self.wait()

    def wait(self) -> None:
        """等待运动结束；带超时，避免 get_run_status 异常时死等。"""
        deadline = time.monotonic() + float(self.move_wait_timeout_sec)
        time.sleep(0.3)
        while self.mc.get_run_status():
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"wait() 超时：{self.move_wait_timeout_sec}s 内 get_run_status 仍为真"
                )
            time.sleep(0.1)
        time.sleep(0.3)

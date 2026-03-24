# -*- coding: utf-8 -*-
"""多机械臂配置：arms.json + 设备工厂（供 pytest 子目录 conftest / Qt 启动器）。"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Callable, Optional

_ROOT = os.path.dirname(os.path.abspath(__file__))
_ARMS_PATH = os.path.join(_ROOT, "arms.json")

DeviceFactory = Callable[[str], Any]
_PROFILE_BUILDERS: dict[str, DeviceFactory] = {}


def _register_profile(name: str, factory: DeviceFactory) -> None:
    _PROFILE_BUILDERS[name] = factory


def _build_pro450(ip: str) -> Any:
    from settings import Mycobot450Base

    return Mycobot450Base(ip=ip if ip.strip() else None)


def _build_mercury_e1(ip: str) -> Any:
    from settings import MercuryE1Base

    port = ip.strip() or os.environ.get("MERCURY_E1_PORT", "").strip() or "com3"
    return MercuryE1Base(port=port)


def _build_mycobot280(ip: str) -> Any:
    from settings import Mycobot280Base

    port = ip.strip() or os.environ.get("MYCOBOT280_PORT", "").strip() or "com5"
    return Mycobot280Base(port=port)


def _build_ultraarm_p1(ip: str) -> Any:
    from settings import UltraArmP1Base

    # ip 字段复用为串口名；留空则用 ULTRAARM_PORT / 默认
    port = ip.strip() or None
    return UltraArmP1Base(port=port)


def _build_mercury(_ip: str) -> Any:
    from settings import MercuryBase

    lp = os.environ.get("MERCURY_LEFT_PORT", "").strip() or "/dev/left_arm"
    rp = os.environ.get("MERCURY_RIGHT_PORT", "").strip() or "/dev/right_arm"
    return MercuryBase(left_port=lp, right_port=rp)


_register_profile("pro450", _build_pro450)
_register_profile("mercury_e1", _build_mercury_e1)
_register_profile("mycobot280", _build_mycobot280)
_register_profile("ultraarm_p1", _build_ultraarm_p1)
_register_profile("mercury", _build_mercury)


class ArmsConfigError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def load_arms_config() -> dict[str, Any]:
    if not os.path.isfile(_ARMS_PATH):
        raise ArmsConfigError(f"未找到配置文件: {_ARMS_PATH}")
    with open(_ARMS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ArmsConfigError("arms.json 根节点必须是对象")
    arms = raw.get("arms")
    if not isinstance(arms, dict) or not arms:
        raise ArmsConfigError("arms.json 必须包含非空 arms 对象")
    for aid, entry in arms.items():
        if not isinstance(entry, dict):
            raise ArmsConfigError(f"arms.{aid} 必须是对象")
        if "device_profile" not in entry or "testcase_roots" not in entry:
            raise ArmsConfigError(f"arms.{aid} 缺少 device_profile 或 testcase_roots")
        roots = entry["testcase_roots"]
        if (
            not isinstance(roots, list)
            or not roots
            or not all(isinstance(x, str) and x.strip() for x in roots)
        ):
            raise ArmsConfigError(f"arms.{aid}.testcase_roots 必须是非空字符串数组")
    return raw


def list_arm_ids() -> list[str]:
    cfg = load_arms_config()
    return sorted(cfg["arms"].keys())


def get_arm_entry(arm_id: str) -> dict[str, Any]:
    cfg = load_arms_config()
    arms = cfg["arms"]
    if arm_id not in arms:
        raise ArmsConfigError(
            f"未知机械臂 ID: {arm_id!r}，可选: {', '.join(sorted(arms.keys()))}"
        )
    return arms[arm_id]


def default_arm_id() -> str:
    cfg = load_arms_config()
    d = cfg.get("default_arm")
    if isinstance(d, str) and d.strip():
        aid = d.strip()
        if aid in cfg["arms"]:
            return aid
    return sorted(cfg["arms"].keys())[0]


def resolve_arm_id(cli_arm: Optional[str] = None) -> str:
    if cli_arm is not None and str(cli_arm).strip() != "":
        aid = str(cli_arm).strip()
        get_arm_entry(aid)
        return aid
    env_arm = os.environ.get("ELEPHANT_ARM", "").strip()
    if env_arm:
        get_arm_entry(env_arm)
        return env_arm
    return default_arm_id()


def resolve_mycobot_ip_chain(explicit: Optional[str] = None) -> str:
    if explicit is not None and str(explicit).strip() != "":
        return str(explicit).strip()
    return (
        os.environ.get("MYCOBOT450_IP", "").strip()
        or os.environ.get("Mycobot450_IP", "").strip()
        or ""
    )


def resolve_device_ip(arm_id: str, cli_ip: Optional[str] = None) -> str:
    """Pro 450：--elephant-ip > 环境变量 > arms default_ip > settings 默认。"""
    from settings import DEFAULT_MYCOBOT450_IP

    if cli_ip is not None and str(cli_ip).strip() != "":
        return str(cli_ip).strip()
    env_ip = resolve_mycobot_ip_chain(None)
    if env_ip:
        return env_ip
    entry = get_arm_entry(arm_id)
    dip = str(entry.get("default_ip", "") or "").strip()
    if dip:
        return dip
    return DEFAULT_MYCOBOT450_IP


def build_device(arm_id: str, connection: str) -> Any:
    """connection：Pro450 为 IP；串口类产品可为串口名，空则读各产品线环境变量。"""
    entry = get_arm_entry(arm_id)
    profile = str(entry["device_profile"]).strip()
    if profile not in _PROFILE_BUILDERS:
        raise ArmsConfigError(
            f"arms.{arm_id}.device_profile={profile!r} 未注册，"
            f"已知: {', '.join(sorted(_PROFILE_BUILDERS.keys()))}"
        )
    return _PROFILE_BUILDERS[profile](connection)


def get_testcase_roots(arm_id: str) -> list[str]:
    entry = get_arm_entry(arm_id)
    return list(entry["testcase_roots"])


def legacy_cases_dir_map(arm_id: Optional[str] = None) -> dict[str, str]:
    aid = arm_id or resolve_arm_id()
    roots = get_testcase_roots(aid)
    return {str(i + 1): path for i, path in enumerate(roots)}


def connection_env_var_for_arm(arm_id: str) -> Optional[str]:
    """Qt 界面提示：覆盖连接参数时写入的环境变量名（mercury 双臂为 None）。"""
    entry = get_arm_entry(arm_id)
    prof = str(entry.get("device_profile", "")).strip()
    return {
        "pro450": "MYCOBOT450_IP",
        "ultraarm_p1": "ULTRAARM_PORT",
        "mercury_e1": "MERCURY_E1_PORT",
        "mycobot280": "MYCOBOT280_PORT",
        "mercury": None,
    }.get(prof)


def get_connection_mode(arm_id: str) -> str:
    """arms.json 的 connection_mode，缺省时按 device_profile 推断：ip / serial / dual_serial。"""
    entry = get_arm_entry(arm_id)
    m = entry.get("connection_mode")
    if m in ("ip", "serial", "dual_serial"):
        return str(m)
    prof = str(entry.get("device_profile", "")).strip()
    if prof == "pro450":
        return "ip"
    if prof == "mercury":
        return "dual_serial"
    return "serial"

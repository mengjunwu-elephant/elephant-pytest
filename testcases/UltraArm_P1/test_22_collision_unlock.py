# -*- coding: utf-8 -*-
import os
import sys
import time
from typing import Any, Optional

import allure
import pytest

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases: list[dict[str, Any]] = get_test_data_from_excel(
    UltraArmP1Base.COLLISION_UNLOCK_DATA_FILE,
    "collision_unlock",
    required_columns=(
        "title",
        "api",
        "target_angles",
        "expect_unlock",
        "expect_data",
        "test_type",
    ),
)


def _wait_tkinter_ok_or_cancel() -> Optional[str]:
    """有桌面环境时弹出「确定/取消」对话框；失败返回 None（调用方做其它回退）。"""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception as e:
        logger.debug("tkinter 未可用: %s", e)
        return None
    text = (
        "请用手或治具做好阻挡，点击「确定」后机械臂将全关节运动（应在阻挡下触发碰撞）。\n"
        "未准备好请点击「取消」以跳过本用例。"
    )
    root = tk.Tk()
    root.withdraw()
    try:
        ok = bool(messagebox.askokcancel("UltraArm P1 碰撞测试", text))
    except Exception as e:
        logger.debug("无法显示确认对话框: %s", e)
        try:
            root.destroy()
        except Exception:
            pass
        return None
    try:
        root.destroy()
    except Exception:
        pass
    return "ok" if ok else "cancel"


def _wait_for_operator_block_ready() -> None:
    """本机终端：input 回车；无 TTY 时试弹窗确定（适合测试资源管理器）；再不行则倒计时。"""
    msg = (
        "请手动阻挡机械臂（末端运动路径），准备好后按回车："
        "机械臂将全关节运动，应在阻挡下触发碰撞。"
    )
    if sys.stdin is not None and sys.stdin.isatty():
        input(msg)
        return
    use_gui = os.environ.get("ELEPHANT_P1_COLLISION_NO_GUI", "").strip() not in (
        "1",
        "true",
        "yes",
    )
    if use_gui:
        with allure.step("无 TTY：弹出确认窗（在阻挡就绪后点确定）"):
            r = _wait_tkinter_ok_or_cancel()
        if r == "ok":
            return
        if r == "cancel":
            pytest.skip("用户点击取消，未执行全关节运动")
    raw = (os.environ.get("ELEPHANT_P1_COLLISION_UNLOCK_PREP_SEC") or "8").strip()
    try:
        sec = float(raw)
    except ValueError:
        sec = 8.0
    with allure.step("非 TTY 且无有效输入方式：按秒数等待（请同期完成阻挡）"):
        logger.info(
            "未检测到 TTY 且未使用 GUI 确认/已禁用，将等待 %.1f 秒后再运动。"
            "可设 ELEPHANT_P1_COLLISION_NO_GUI=0 尝试弹窗，或设 ELEPHANT_P1_COLLISION_UNLOCK_PREP_SEC。",
            sec,
        )
        if sec > 0:
            time.sleep(sec)
        else:
            logger.info("ELEPHANT_P1_COLLISION_UNLOCK_PREP_SEC=0，不等待，立即开始运动。")


@pytest.fixture(autouse=True)
def reset_device(device: Any) -> None:
    yield
    device.mc.clear_error_status()
    device.go_zero()


@allure.feature("碰撞检测后解锁")
@allure.story("手动阻挡后 collision_unlock 与 get_error_information")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if (c.get("test_type") or "").strip() == "manual"],
    ids=lambda c: c["title"],
)
def test_collision_unlock(device: Any, case: dict[str, Any]) -> None:
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'target_angles: {case["target_angles"]}')
    logger.debug(f'speed: {case["speed"]}')
    logger.debug(f'expect_unlock: {case["expect_unlock"]}')
    logger.debug(f'expect_data: {case["expect_data"]}')

    speed = int(case["speed"]) if case.get("speed") is not None else int(device.speed)
    expect_unlock = int(case["expect_unlock"])
    expect_data = int(case["expect_data"])
    angles: list = eval(str(case["target_angles"]))

    with allure.step("前置：清除错误并运动至标定参考姿态（coords_init_angles）"):
        device.mc.clear_error_status()
        device.mc.set_angles(device.coords_init_angles, device.speed)
        device.wait()

    _wait_for_operator_block_ready()

    with allure.step("全关节运动（应在阻挡下触发碰撞）"):
        device.mc.set_angles(angles, speed)
        device.wait()
        time.sleep(0.3)

    with allure.step("调用 get_error_information，确认已上报碰撞/错误（非 0）"):
        err_before = int(device.mc.get_error_information())
        allure.attach(str(err_before), name="碰撞/错误码", attachment_type=allure.attachment_type.TEXT)
        assert err_before != 0, (
            f"未检测到非零错误码，请确认已阻挡并触发碰撞；当前 get_error_information={err_before!r}"
        )

    with allure.step("调用 collision_unlock，确认返回 1"):
        unlock_res = int(device.mc.collision_unlock())
        allure.attach(str(unlock_res), name="collision_unlock 返回", attachment_type=allure.attachment_type.TEXT)
        assert unlock_res == expect_unlock, (
            f"collision_unlock 返回异常，期望 {expect_unlock!r}，实际 {unlock_res!r}"
        )

    with allure.step("再次调用 get_error_information，确认为 0（无报错）"):
        err_after = int(device.mc.get_error_information())
        allure.attach(str(expect_data), name="期望错误码", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(err_after), name="实际错误码", attachment_type=allure.attachment_type.TEXT)
        assert err_after == expect_data, (
            f"解锁后错误码不符合预期，期望 {expect_data!r}，实际 {err_after!r}"
        )

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

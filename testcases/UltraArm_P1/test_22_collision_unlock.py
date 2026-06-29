# -*- coding: utf-8 -*-
import time
from typing import Any

import allure
import pytest

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases: list[dict[str, Any]] = get_test_data_from_excel(
    UltraArmP1Base.TEST_DATA_FILE,
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

    prompt_continue(
        "请手动阻挡机械臂（末端运动路径），准备好后按回车："
        "机械臂将全关节运动，应在阻挡下触发碰撞。",
        title="UltraArm P1 碰撞测试",
    )

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

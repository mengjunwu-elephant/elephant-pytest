# -*- coding: utf-8 -*-
from __future__ import annotations

import ast
import time
from typing import Any

import allure
import pytest

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据（sheet：get_motor_enable_status）
cases = get_test_data_from_excel(
    UltraArmP1Base.TEST_DATA_FILE,
    "get_motor_enable_status",
    required_columns=("title", "api", "expect_data", "test_type"),
)


def _expect_list(test_type: str) -> list[int]:
    for c in cases:
        if (c.get("test_type") or "").strip() != test_type:
            continue
        raw = str(c.get("expect_data") or "").strip()
        if not raw:
            continue
        return [int(float(x)) for x in ast.literal_eval(raw)]
    raise RuntimeError(
        f"Excel get_motor_enable_status 缺少 test_type={test_type!r} 且 expect_data 非空的行"
    )


EXP_ENABLED = _expect_list("enabled")
EXP_RELEASED = _expect_list("released")


def _normalize_motor_status(resp: Any) -> list[int] | None:
    if resp in (-1, None):
        return None
    if isinstance(resp, (list, tuple)):
        return [int(round(float(x))) for x in resp]
    return None


@pytest.fixture(scope="module", autouse=True)
def _teardown_set_joint_enable(device):
    """模块结束后上使能锁紧，再交由 device 关闭串口。"""
    yield
    with allure.step("测试模块结束：set_joint_enable() 锁紧机械臂"):
        try:
            device.mc.set_joint_enable()
            time.sleep(1.0)
            logger.info("模块收尾已调用 set_joint_enable()")
        except Exception as e:
            logger.warning(f"模块收尾 set_joint_enable 异常：{e}")


@allure.feature("电机使能状态")
@allure.story("get_motor_enable_status 与掉使能/上使能")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if (c.get("test_type") or "").strip() == "flow"],
    ids=lambda c: c["title"],
)
def test_get_motor_enable_status_flow(device, case):
    """顺序验证：上使能列表 → 掉使能 → 全 0 → 再上使能恢复列表。"""
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'期望enabled:{EXP_ENABLED}')
    logger.debug(f'期望released:{EXP_RELEASED}')

    with allure.step("正常使能状态：get_motor_enable_status"):
        r0 = device.mc.get_motor_enable_status()
        logger.debug(f"接口返回：{r0}")
        act0 = _normalize_motor_status(r0)
        assert act0 is not None, f"读取失败，返回值：{r0!r}"
        allure.attach(str(EXP_ENABLED), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(act0), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert act0 == EXP_ENABLED, f"用例【{title}】断言失败，期望 {EXP_ENABLED}，实际 {act0}"

    with allure.step("调用 set_joint_release() 掉使能"):
        device.mc.set_joint_release()
        time.sleep(2.0)

    with allure.step("掉使能后：get_motor_enable_status"):
        r1 = device.mc.get_motor_enable_status()
        logger.debug(f"接口返回：{r1}")
        act1 = _normalize_motor_status(r1)
        assert act1 is not None, f"读取失败，返回值：{r1!r}"
        allure.attach(str(EXP_RELEASED), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(act1), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert act1 == EXP_RELEASED, f"用例【{title}】断言失败，期望 {EXP_RELEASED}，实际 {act1}"

    with allure.step("调用 set_joint_enable() 上使能锁紧"):
        ret = device.mc.set_joint_enable()
        logger.debug(f"接口返回：{ret}")
        time.sleep(2.0)

    with allure.step("再次查询：应恢复上使能列表"):
        r2 = device.mc.get_motor_enable_status()
        logger.debug(f"接口返回：{r2}")
        act2 = _normalize_motor_status(r2)
        assert act2 is not None, f"读取失败，返回值：{r2!r}"
        allure.attach(str(EXP_ENABLED), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(act2), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert act2 == EXP_ENABLED, f"用例【{title}】断言失败，期望 {EXP_ENABLED}，实际 {act2}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

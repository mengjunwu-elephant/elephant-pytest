# -*- coding: utf-8 -*-
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_uart1_communication")


@allure.feature("设置串口1通信")
@allure.story("正确设置串口1通信")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_uart1_communication(device, case):
    title = case["title"]
    expected = case["expect_data"]
    state = case["state"]
    restore_state = case["restore_state"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'state:{state}')
    logger.debug(f'restore_state:{restore_state}')

    try:
        with allure.step(f"调用 {case['api']} 接口"):
            set_res = device.mc.set_uart1_communication(state)
            logger.debug(f"接口返回：{set_res}")

        with allure.step("断言接口返回结果"):
            allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
            allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
            assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

        logger.info(f'✅ 用例【{title}】测试通过')
    finally:
        if restore_state is not None:
            with allure.step(f"恢复串口1通信状态为 {restore_state}"):
                device.mc.set_uart1_communication(restore_state)
                logger.debug(f"已恢复 state={restore_state}")

    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置串口1通信")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_uart1_communication_exception(device, case):
    title = case["title"]
    state = case["state"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'state:{state}')

    with allure.step(f"断言抛出 ultraArmP1DataException，状态为 {state}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_uart1_communication(state)

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

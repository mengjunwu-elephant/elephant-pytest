# -*- coding: utf-8 -*-
import time
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.operator_input import prompt_continue, prompt_text
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_digital_io_output")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理；数字 IO 与底座 IO 共用底座，teardown 时复位底座 IO。"""
    dev = UltraArmP1Base()
    logger.info("初始化完成，接口测试开始")
    prompt_continue("请确认数字IO测试工具已连接，点击回车继续测试")
    yield dev
    dev.default_digital_io_output()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置数字IO输出")
@allure.story("正确设置数字IO输出")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_digital_io_output_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")
    logger.debug(f"test_api:{case['api']}")
    logger.debug(f"pin_no:{case['pin_no']}, state:{case['state']}")

    with allure.step(f"调用 {case['api']} 接口"):
        time.sleep(1)
        set_res = device.mc.set_digital_io_output(case["pin_no"], case["state"])
        logger.debug(f"接口返回：{set_res}")

    with allure.step("读取数字IO状态"):
        if case["pin_no"] == 3:
            get_res = device.mc.get_end_io_state(1)
        elif case["pin_no"] == 4:
            get_res = device.mc.get_end_io_state(2)
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(set_res, str), f"返回类型错误，应为 int，实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言数字IO状态与设置一致"):
        allure.attach(str(case["state"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert case["state"] == get_res, f"用例【{title}】断言失败，期望 {case['state']}，实际 {get_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")


@allure.feature("设置数字IO输出")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_digital_io_output_exception(device, case):
    title = case["title"]

    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")
    logger.debug(f"test_api:{case['api']}, pin_no:{case['pin_no']}, state:{case['state']}")

    with allure.step(f"断言抛出 ultraArmP1DataException，引脚为 {case['pin_no']}，状态为 {case['state']}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_digital_io_output(case["pin_no"], case["state"])

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

import time

import pytest
import allure
from pymycobot.error import MyCobot280DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "focus_servo")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("单个电机上电")
@allure.story("设置单个电机上电")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_focus_servo(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_joint:{case["joint"]}')

    with allure.step("放松对应关节"):
        device.mc.release_servo(case['joint'])

    with allure.step("调用 focus_servo 接口"):
        response = device.mc.focus_servo(case['joint'])
        logger.debug(f"接口返回：{response}")

    with allure.step(f'手动查看{case["joint"]}关节舵机是否锁紧'):
        input(f'请手动拖动{case["joint"]}关节舵机，查看是否锁紧,按回车键继续')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("单个电机上电")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_focus_servo_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，关节: {case['joint']}")

    with allure.step("断言抛出 MyCobot280DataException"):
        with pytest.raises(MyCobot280DataException) as exc:
            device.mc.focus_servo(case['joint'])

    logger.info(f"✅ 用例【{title}】异常测试通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

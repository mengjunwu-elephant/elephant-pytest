import time
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_angles")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = UltraArmP1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置关节全角度")
@allure.story("正确设置全角度")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_angles0(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'angles:{case["angles"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_angles(eval(case["angles"]),case["speed"])
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f'调用 get_angles_info 接口'):
        get_res = device.mc.get_angles_info()
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言 get_angles_info 返回值"):
        allure.attach(str(case["angles"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, eval(case["angles"]), 1,'设置全角度'), f"用例【{title}】断言失败，期望 {case['angles']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置关节全角度")
@allure.story("超限报错验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_angles_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'angles:{case["angles"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"断言抛出 ultraArmP1DataException,角度为{case['angles']}, 速度为{case['speed']}"):
        with pytest.raises(ultraArmP1DataException):
            device.mc.set_angles(eval(case["angles"]), case["speed"])
            device.wait()

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

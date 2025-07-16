import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "set_fresh_mode")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.m.power_on()
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置运动模式")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_set_fresh_mode1(device, case):
    title = case["title"]
    expected = case["expect_data"]
    mode = case["mode"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_mode:{case["mode"]}')

    with allure.step("调用 set_fresh_mode 接口, mode = {case['mode']}"):
        set_res = device.m.set_fresh_mode(mode)
        time.sleep(0.1)
        get_res = device.m.get_fresh_mode()
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言设置返回值"):
        allure.attach(str(expected), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言获取返回值"):
        allure.attach(str(mode), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == mode, f"用例【{title}】断言失败，期望 {expected}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置运动模式")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_set_fresh_mode2(device, case):
    title = case["title"]
    mode = case["mode"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_mode:{case["mode"]}')

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.set_fresh_mode(mode)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
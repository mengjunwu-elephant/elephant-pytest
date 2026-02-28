import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "set_digital_output")


normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.m.send_angles([90,0,90,0,0,0], dev.speed)
    input('请确认已连接IO测试工具,按回车键继续')
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置末端IO")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_set_digital_output1(device, case):
    title = case["title"]
    expected_1 = case["expect_data_1"]
    pin_no = case["pin_no"]
    pin_signal = case["pin_signal"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 set_digital_output 接口"):
        set_res = device.m.set_digital_output(pin_no, pin_signal)
        time.sleep(0.1)
        get_res = device.m.get_digital_input(pin_no)
        logger.debug(f"set_res返回:{set_res},get_res:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言 set_digital_output 返回结果"):
        allure.attach(str(expected_1), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    with allure.step("断言 get_digital_input 返回结果"):
        allure.attach(str(pin_signal), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == pin_signal, f"用例【{title}】断言失败，期望 {pin_signal}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置超限末端IO")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_set_digital_output2(device, case):
    title = case["title"]
    pin_no = case["pin_no"]
    pin_signal = case["pin_signal"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.set_digital_output(pin_no, pin_signal)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "set_servo_data")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
logic_cases = [case for case in cases if case.get("test_type") == "logic"]
exception_cases_1 = [case for case in cases if case.get("test_type") == "exception_1"]
exception_cases_2 = [case for case in cases if case.get("test_type") == "exception_2"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置舵机参数")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_set_servo_data1(device, case):
    title = case["title"]
    expected_1 = case["expect_data_1"]
    expected_2 = case["expect_data_2"]
    joint = case["joint"]
    data_id = case["data_id"]
    value = case["value"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 set_servo_data 接口"):
        set_res = device.m.set_servo_data(joint, data_id, value)
        time.sleep(0.1)
        get_res = device.m.get_servo_data(joint, data_id)
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言 set_servo_data 返回结果"):
        allure.attach(str(expected_1), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    with allure.step("断言 get_servo_data 返回结果"):
        allure.attach(str(expected_2), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == expected_2, f"用例【{title}】断言失败，期望 {expected_2}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置回原舵机参数")
@allure.story("正常用例")
@pytest.mark.parametrize("case", logic_cases, ids=[case["title"] for case in logic_cases])
def test_set_servo_data2(device, case):
    title = case["title"]
    expected_1 = case["expect_data_1"]
    expected_2 = case["expect_data_2"]
    joint = case["joint"]
    data_id = case["data_id"]
    value = case["value"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 set_servo_data 接口"):
        set_res = device.m.set_servo_data(joint, data_id, value)
        time.sleep(0.1)
        get_res = device.m.get_servo_data(joint, data_id)
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言 set_servo_data 返回结果"):
        allure.attach(str(expected_1), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    with allure.step("断言 get_servo_data 返回结果"):
        allure.attach(str(expected_2), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == expected_2, f"用例【{title}】断言失败，期望 {expected_2}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置舵机参数超限")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases_1, ids=[case["title"] for case in exception_cases_1])
def test_set_servo_data3(device, case):
    title = case["title"]
    joint = case["joint"]
    data_id = case["data_id"]
    value = case["value"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.set_servo_data(joint, data_id, value)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置舵机参数超限")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases_2, ids=[case["title"] for case in exception_cases_2])
def test_set_servo_data4(device, case):
    title = case["title"]
    joint = case["joint"]
    data_id = case["data_id"]
    value = case["value"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with pytest.raises(ValueError, match=".*"):
        device.m.set_servo_data(joint, data_id, value)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
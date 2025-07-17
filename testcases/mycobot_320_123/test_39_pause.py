import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base


# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "pause")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    yield dev
    dev.m.set_fresh_mode(0)
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("控制指令暂停核心并停止所有运动指令")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_pause1(device, case):
    ID = case["ID"]
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('控制机械臂运动'):


    with allure.step(f"调用 pause 接口"):
        set_res = device.m.pause()
        get_res = device.m.is_paused()
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言pause返回值"):
        allure.attach(str(expected), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言is_paused返回值"):
        allure.attach(str(expected), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


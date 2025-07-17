import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base


# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "is_paused")

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

@allure.feature("检查程序是否暂停移动命令")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_is_paused1(device, case):
    ID = case["ID"]
    title = case["title"]
    expected_1 = case["expect_data_1"]
    expected_2 = case["expect_data_2"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('控制机械臂运动'):
        device.different_modes(ID)

    with allure.step(f"调用 is_paused 接口"):
        device.m.pause()
        get_res_1 = device.m.is_paused()
        device.m.resume()
        get_res_2 = device.m.is_paused()
        logger.debug(f"get_res_1暂停运动后返回:{get_res_1},get_res_2恢复暂停后返回:{get_res_2}")

    with allure.step("断言暂停运动后返回值类型为 int"):
        assert isinstance(get_res_1, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(get_res_1)}"

    with allure.step("断言恢复暂停后返回值类型为 int"):
        assert isinstance(get_res_2, int), f"返回类型错误,应为{type(expected_2)},实际为 {type(get_res_2)}"

    with allure.step("断言暂停运动后is_paused返回值"):
        allure.attach(str(expected_1), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res_1), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res_1 == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {get_res_1}"

    with allure.step("断言恢复暂停后is_paused返回值"):
        allure.attach(str(expected_2), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res_2), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res_2 == expected_2, f"用例【{title}】断言失败，期望 {expected_2}，实际 {get_res_2}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


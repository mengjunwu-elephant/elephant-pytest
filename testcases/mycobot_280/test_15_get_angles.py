import time

import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "get_angles")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取机械臂全角度")
@allure.story("不同运动模式下获取角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_angles(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_data:{case["angles"]}')

    with allure.step("设置运动模式"):
        device.mc.set_free_mode(case["fresh_mode"])
        logger.debug(f"设置运动模式为：{case['fresh_mode']}")
        allure.attach(str(case["fresh_mode"]), name="运动模式", attachment_type=allure.attachment_type.TEXT)

    with allure.step("调用 send_angles 接口"):
        device.mc.send_angles(eval(case["angles"]),device.speed)
        device.wait()
        logger.debug(f"angles：{case['angles']}")
        allure.attach(str(case["angles"]), name="angles", attachment_type=allure.attachment_type.TEXT)

    with allure.step("调用 get_angles 接口"):
        response = device.mc.get_angles()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,eval(expected),tol=2,name='获取全角度'), f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

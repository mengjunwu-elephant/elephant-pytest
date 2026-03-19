import time
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "get_coords_info")


@allure.feature("读取全关节坐标")
@allure.story("（读取全关节坐标")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_coords_info1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('使机械臂运动到指定全坐标'):
        device.mc.set_coords(eval(expected), device.speed)

    with allure.step(f"调用 {case['api']} 接口"):
        if case['parameter'] is not None:
            response = device.mc.get_coords_info(eval(case['parameter']))
        else:
            response = device.mc.get_coords_info()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,eval(expected),tol=0.2,name='获取全关节坐标'), f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')



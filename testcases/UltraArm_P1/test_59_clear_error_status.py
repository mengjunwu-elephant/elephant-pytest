import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "clear_error_status")


@allure.feature("清除错误状态")
@allure.story("无异常状态清除")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal2"], ids=lambda c: c["title"])
def test_clear_error_status_no_error(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.clear_error_status()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert str(response).lower() == str(expected).lower(), (
            f"用例【{title}】断言失败，期望 {expected},实际 {response}"
        )

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "get_digital_inputs")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    input('请确认底座IO测试工具已连接,点击回车继续测试')
    yield dev
    dev.default_digital_io_output()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("读取末端所有IO输入")
@allure.story("正确读取末端IO输入")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_digital_inputs1(device, case):
    title = case["title"]
    expected = eval(case["expect_data"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.get_digital_inputs()
        time.sleep(1)
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


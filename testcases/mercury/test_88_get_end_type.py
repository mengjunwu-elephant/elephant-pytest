import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_end_type")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取末端类型")
@allure.story("正常用例 - 获取机械臂末端类型")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_end_type(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")

    with allure.step("获取机械臂末端类型"):
        response = device.mc.get_end_type()
    with allure.step("断言返回类型为int"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"

    with allure.step("断言返回结果与期望值一致"):
        assert response == case['l_expect_data'], f"机械臂期望={case['l_expect_data']}，实际={response}"

    logger.info(f"请求结果断言成功,用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

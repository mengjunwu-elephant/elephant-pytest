import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_end_type")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取末端类型")
@allure.story("正常用例 - 获取左右臂末端类型")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_end_type(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")

    with allure.step("获取左臂末端类型"):
        l_response = device.ml.get_end_type()

    with allure.step("获取右臂末端类型"):
        r_response = device.mr.get_end_type()

    with allure.step("断言返回类型为int"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言返回结果与期望值一致"):
        assert l_response == case['l_expect_data'], f"左臂期望={case['l_expect_data']}，实际={l_response}"
        assert r_response == case['r_expect_data'], f"右臂期望={case['r_expect_data']}，实际={r_response}"

    logger.info(f"请求结果断言成功,用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

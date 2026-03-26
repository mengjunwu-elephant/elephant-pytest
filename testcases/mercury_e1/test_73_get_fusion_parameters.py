import time
import pytest
import allure
from pymycobot.error import MercuryE1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryE1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MercuryE1Base.TEST_DATA_FILE, "get_fusion_parameters")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = MercuryE1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    # dev.go_zero()
    # dev.wait()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取速度融合规划参数")
@allure.story("正确获取速度融合规划参数")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_fusion_parameters1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'rank:{case["rank"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.get_fusion_parameters(case['rank'])
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected,f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("获取速度融合规划参数")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_fusion_parameters_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'rank:{case["rank"]}')

    with allure.step(f"断言抛出 MercuryE1DataException,参数为{case['rank']}"):
        with pytest.raises(MercuryE1DataException) as exc:
            device.mc.get_fusion_parameters(case['rank'])

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
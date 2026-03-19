import pytest
import allure
from pymycobot.error import MercuryDataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.PRO_GRIPPER_TEST_DATA_FILE, "get_pro_gripper")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取Pro夹爪参数")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_pro_gripper(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("调用接口获取夹爪状态"):
        response = device.mc.get_pro_gripper(case['parameter'])
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "接口返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回值类型为 int"):
        if case['parameter'] == 1:
            assert isinstance(response, float), f"返回类型错误，实际为 {type(response)}"
        else:
            assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值与期望值相符"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取Pro夹爪参数")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_pro_gripper_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step(f"断言设置 Pro 夹爪参数时抛出 MercuryDataException,address为{case['parameter']}"):
        with pytest.raises(MercuryDataException):
            device.mc.get_pro_gripper(case["parameter"])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

# 从 Excel 中提取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_pro_gripper_speed")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_pro_gripper_speed(100)
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置Pro夹爪速度")
@allure.story("设置合法速度值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_pro_gripper_speed_valid(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case.get('parameter')}")

    with allure.step("调用 set_pro_gripper_speed 接口"):
        response = device.mc.set_pro_gripper_speed(case["parameter"])
        allure.attach(str(response), "返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(response),'实际值',allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置Pro夹爪速度")
@allure.story("设置非法速度值触发异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_pro_gripper_speed_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case.get('parameter')}")

    with allure.step(f"调用接口并断言抛出 MercuryDateException 异常,速度为{case['parameter']}"):
        with pytest.raises(MercuryDataException):
            device.mc.set_pro_gripper_speed(case["parameter"])

    logger.info(f"✅ 用例【{case['title']}】触发异常测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

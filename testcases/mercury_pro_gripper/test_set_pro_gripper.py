import pytest
import allure
from pymycobot.error import MercuryDataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置Pro夹爪参数")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_pro_gripper_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step("调用接口设置 Pro 夹爪参数"):
        set_res = device.ml.set_pro_gripper(case["parameter"], case["value"])
        allure.attach(str(set_res), "设置接口返回值", allure.attachment_type.TEXT)

    with allure.step("调用接口获取 Pro 夹爪参数"):
        get_res = device.ml.get_pro_gripper(case["parameter"])
        allure.attach(str(get_res), "获取接口返回值", allure.attachment_type.TEXT)

    with allure.step("断言设置接口返回值为 int"):
        assert isinstance(set_res, int), f"返回类型错误，实际为 {type(set_res)}"

    with allure.step("断言设置接口返回值正确"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取接口返回值正确"):
        allure.attach(str(case['parameter']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(get_res),'实际值',allure.attachment_type.TEXT)
        assert get_res == case["parameter"], f"期望：{case['parameter']}，实际：{get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")


@allure.feature("设置Pro夹爪参数")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_pro_gripper_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step(f"断言设置 Pro 夹爪参数时抛出 MercuryDataException,address为{case['parameter']},value为{case['value']}"):
        with pytest.raises(MercuryDataException):
            device.ml.set_pro_gripper(case["parameter"], case["value"])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

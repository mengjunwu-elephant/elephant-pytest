import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_enabled")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪使能")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_enabled_normal(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("调用接口设置夹爪使能"):
        set_res = device.ml.set_hand_gripper_enabled(case["parameter"])

    with allure.step("断言返回类型为int"):
        assert isinstance(set_res, int), f"返回类型错误，实际类型为 {type(set_res)}"

    with allure.step("断言返回值符合预期"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case['expect_data'], f"期望：{case['expect_data']}，实际：{set_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")

@allure.feature("设置夹爪使能")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_enabled_exception(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step(f"调用接口，期望触发 MercuryDataException 异常, 参数为 {case['parameter']}"):
        with pytest.raises(MercuryDataException):
            device.ml.set_hand_gripper_enabled(case["parameter"])

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "get_hand_gripper_min_pressure")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    dev.set_default_mini_pressure()
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]

@allure.feature("获取夹爪最小启动力")
@allure.story("获取夹爪最小启动力")
@pytest.mark.parametrize("case", normal_cases, ids=lambda c: c["title"])
def test_get_hand_gripper_min_pressure_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")

    with allure.step("调用 get_hand_gripper_min_pressure 接口"):
        response = device.mc.get_hand_gripper_min_pressure(case["joint"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回结果与预期一致"):
        allure.attach(str(case['expect_data']), "期望数据", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际结果", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望: {case['expect_data']}，实际: {response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取夹爪最小启动力")
@allure.story("获取夹爪最小启动力-异常场景")
@pytest.mark.parametrize("case", exception_cases, ids=lambda c: c["title"])
def test_get_hand_gripper_min_pressure_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")

    with allure.step(f"调用接口并期待抛出 MercuryDataException,关节为{case['joint']}"):
        with pytest.raises(MercuryDataException, match=f".*"):
            device.mc.get_hand_gripper_min_pressure(case['joint'])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

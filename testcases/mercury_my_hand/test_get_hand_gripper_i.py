import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 获取用例数据
cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "get_hand_gripper_i")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取单关节I值")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_hand_gripper_i_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")

    with allure.step("调用 get_hand_gripper_i"):
        response = device.ml.get_hand_gripper_i(case["joint"])

    with allure.step("校验返回类型"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("校验返回值正确"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")


@allure.feature("获取单关节I值")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_hand_gripper_i_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")

    with allure.step(f"调用 get_hand_gripper_i 并验证抛出异常,关节为{case['joint']}"):
        with pytest.raises(MercuryDataException):
            device.ml.get_hand_gripper_i(int(case["joint"]))

    logger.info(f"✅ 异常断言成功，用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

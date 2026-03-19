import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_cww")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_cww()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪逆时针可运行误差")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_counterclockwise_normal(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    logger.debug(f"test_api:{case['api']}")
    logger.debug(f"test_joint:{case['joint']}")
    logger.debug(f"test_parameter:{case['parameter']}")

    with allure.step("调用接口设置夹爪逆时针可运行误差"):
        set_res = device.mc.set_hand_gripper_counterclockwise(case["joint"], case["parameter"])
        get_res = device.mc.get_hand_gripper_counterclockwise(case["joint"])

    with allure.step("断言设置接口返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，实际类型为 {type(set_res)}"

    with allure.step("断言设置接口返回值符合预期"):
        allure.attach(str(case["expect_data"]),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取接口返回的逆时针可运行误差"):
        allure.attach(str(case["parameter"]),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(get_res),'实际值',allure.attachment_type.TEXT)
        assert get_res == case["parameter"], f"断言失败，期望：{case['parameter']}，实际：{get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")

@allure.feature("设置夹爪逆时针可运行误差")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_counterclockwise_exception(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    logger.debug(f"test_api:{case['api']}")
    logger.debug(f"test_joint:{case['joint']}")
    logger.debug(f"test_parameter:{case['parameter']}")

    with allure.step(f"调用接口，预期抛出 MercuryDataException,关节为{case['joint']}，逆时针可运行误差为{case['parameter']}"):
        with pytest.raises(MercuryDataException, match=f".*"):
            device.mc.set_hand_gripper_counterclockwise(case["joint"], case["parameter"])

    logger.info(f"✅ 异常断言成功，用例【{case['title']}】测试成功")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")

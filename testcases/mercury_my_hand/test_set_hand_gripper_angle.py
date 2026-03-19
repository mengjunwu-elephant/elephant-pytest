import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger, assert_almost_equal
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_angle")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束复位夹爪角度
    for i in range(6):
        dev.mc.set_hand_gripper_angle(i + 1, 0)
        sleep(2)
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪角度")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_angle_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")
    logger.debug(f"test_angle: {case['angle']}")

    with allure.step("调用接口设置夹爪角度"):
        set_res = device.mc.set_hand_gripper_angle(case["joint"], case["angle"])
        sleep(2)

    with allure.step("调用接口获取夹爪角度"):
        get_res = device.mc.get_hand_gripper_angle(case["joint"])

    with allure.step("断言设置接口返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，实际为 {type(set_res)}"

    with allure.step("断言设置接口返回值正确"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(set_res), "实际值", allure.attachment_type.TEXT)
        assert set_res == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取接口返回的角度正确"):
        allure.attach(str(case['angle']), "期望角度", allure.attachment_type.TEXT)
        allure.attach(str(get_res), "实际角度", allure.attachment_type.TEXT)
        assert_almost_equal(get_res,case["angle"],tol=5,name='设置三指三关节角度'), f"断言失败，期望：{case['angle']}，实际：{get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置夹爪角度")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_angle_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")
    logger.debug(f"test_angle: {case['angle']}")

    with allure.step(f"调用接口设置夹爪角度，预期抛出 MercuryDataException,关节为{case['joint']}，角度为{case['angle']}"):
        with pytest.raises(MercuryDataException):
            device.mc.set_hand_gripper_angle(case["joint"], case["angle"])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

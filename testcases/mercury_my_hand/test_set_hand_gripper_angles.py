import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_angles")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束复位夹爪角度
    dev.ml.set_hand_gripper_angles([0, 0, 0, 0, 0, 0], dev.speed)
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪多个角度")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_angles_normal(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_angles: {case['angles']}")
    logger.debug(f"test_speed: {case['speed']}")

    angles = eval(case["angles"])

    with allure.step("调用接口设置多个夹爪角度"):
        set_res = device.ml.set_hand_gripper_angles(angles, case["speed"])
        sleep(3)

    with allure.step("调用接口获取多个夹爪角度"):
        get_res = device.ml.get_hand_gripper_angles()

    with allure.step("断言设置接口返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，实际类型为 {type(set_res)}"

    with allure.step("断言设置接口返回值正确"):
        assert set_res == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取接口返回的角度正确"):
        allure.attach(str(angles), "期望角度列表", allure.attachment_type.TEXT)
        allure.attach(str(get_res), "实际角度列表", allure.attachment_type.TEXT)
        assert get_res == angles, f"断言失败，期望：{angles}，实际：{get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")

    sleep(5)  # 原 tearDown 中的等待

@allure.feature("设置夹爪多个角度")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_angles_exception(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_angles: {case['angles']}")
    logger.debug(f"test_speed: {case['speed']}")

    angles = eval(case["angles"])

    with allure.step(f"调用接口，预期抛出 MercuryDataException,角度为{angles},速度为{case['speed']}"):
        with pytest.raises(MercuryDataException, match=f".*"):
            device.ml.set_hand_gripper_angles(angles, case["speed"])

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》》》用例【{case['title']}】测试完成《《《《《")

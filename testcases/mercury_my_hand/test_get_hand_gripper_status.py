import pytest
import allure
import time
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "get_hand_gripper_status")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_hand_gripper_angles([0, 0, 0, 0, 0, 0], dev.speed)
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取夹爪状态")
@allure.story("夹爪状态-静止")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 0], ids=lambda c: c["title"])
def test_get_hand_gripper_status_0(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("设置夹爪角度到静止状态"):
        device.mc.set_hand_gripper_angles([10, 60, 10, 10, 10, 10], 5)

    with allure.step("调用 get_hand_gripper_status 获取状态"):
        response = device.mc.get_hand_gripper_status()

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取夹爪状态")
@allure.story("夹爪状态-运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 1], ids=lambda c: c["title"])
def test_get_hand_gripper_status_1(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("等待夹爪运动完成"):
        time.sleep(5)

    with allure.step("调用 get_hand_gripper_status 获取状态"):
        response = device.mc.get_hand_gripper_status()

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取夹爪状态")
@allure.story("夹爪状态-夹持到物体")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 2], ids=lambda c: c["title"])
def test_get_hand_gripper_status_2(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    input("请放置物体到夹爪中间后，按回车继续...")

    with allure.step("设置夹爪角度夹持物体"):
        device.mc.set_hand_gripper_angles([30, 70, 70, 90, 70, 70], 100)
        time.sleep(3)

    with allure.step("调用 get_hand_gripper_status 获取状态"):
        response = device.mc.get_hand_gripper_status()

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取夹爪状态")
@allure.story("夹爪状态-夹持到物体后掉落")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 3], ids=lambda c: c["title"])
def test_get_hand_gripper_status_3(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    input("请取下夹爪夹取的物体后，按回车继续...")

    with allure.step("调用 get_hand_gripper_status 获取状态"):
        response = device.mc.get_hand_gripper_status()

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

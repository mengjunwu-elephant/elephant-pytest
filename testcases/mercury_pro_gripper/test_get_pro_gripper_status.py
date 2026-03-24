import pytest
import allure
from time import sleep
from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.PRO_GRIPPER_TEST_DATA_FILE, "get_pro_gripper_status")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.ml.set_pro_gripper_close()  # 回到零位
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def delay_each_case():
    yield
    sleep(3)

@allure.feature("获取Pro夹爪状态")
@allure.story("运动状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 0], ids=lambda c: c["title"])
def test_get_pro_gripper_status_0(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']} | test_parameters: {case['parameter']}")

    with allure.step("设置夹爪参数为 (100, 5)"):
        device.ml.set_gripper_value(100, 5)
        sleep(0.2)

    with allure.step("获取夹爪状态"):
        response = device.ml.get_pro_gripper_status()
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取Pro夹爪状态")
@allure.story("静止状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 1], ids=lambda c: c["title"])
def test_get_pro_gripper_status_1(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']} | test_parameters: {case['parameter']}")

    with allure.step("等待 5 秒模拟空闲状态"):
        sleep(5)

    with allure.step("获取夹爪状态"):
        response = device.ml.get_pro_gripper_status()
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回结果"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取Pro夹爪状态")
@allure.story("夹取到物体")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 2], ids=lambda c: c["title"])
def test_get_pro_gripper_status_2(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']} | test_parameters: {case['parameter']}")

    with allure.step("人工放置物体，准备夹取"):
        print("请放置物体到夹爪中间后，点击回车开始测试")
        input()

    with allure.step("设置夹爪参数为 (0, 100)"):
        device.ml.set_gripper_value(0, 100)
        sleep(3)

    with allure.step("获取夹爪状态"):
        response = device.ml.get_pro_gripper_status()
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取Pro夹爪状态")
@allure.story("夹取物体后检测到掉落")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 3], ids=lambda c: c["title"])
def test_get_pro_gripper_status_3(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']} | test_parameters: {case['parameter']}")

    with allure.step("人工取下夹爪物体"):
        print("请取下夹爪夹取的物体后，点击回车开始测试")
        input()

    with allure.step("获取夹爪状态"):
        response = device.ml.get_pro_gripper_status()
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

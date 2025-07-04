import pytest
import allure
from time import sleep
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "get_gripper_status")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("夹爪状态接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 0], ids=lambda c: c["title"])
def test_get_gripper_status_0(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameters:{case["parameter"]}')

    with allure.step("设置夹爪角度 [10, 60, 10, 10, 10, 10]，速度 5"):
        device.m.set_gripper_angles([10, 60, 10, 10, 10, 10], 5)

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回: {response}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际类型 {type(response)}"

    with allure.step("断言返回值与预期相等"):
        assert response == case["expect_data"], f"期望 {case['expect_data']}，实际 {response}"

@allure.feature("夹爪状态接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 1], ids=lambda c: c["title"])
def test_get_gripper_status_1(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameters:{case["parameter"]}')

    sleep(5)  # 等待

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回: {response}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际类型 {type(response)}"

    with allure.step("断言返回值与预期相等"):
        assert response == case["expect_data"], f"期望 {case['expect_data']}，实际 {response}"

@allure.feature("夹爪状态接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 2], ids=lambda c: c["title"])
def test_get_gripper_status_2(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameters:{case["parameter"]}')

    # 交互提示
    print("请放置物体到夹爪中间后，按 Enter 继续...")
    input()

    with allure.step("设置夹爪角度 [30, 70, 70, 90, 70, 70]，速度 100"):
        device.m.set_gripper_angles([30, 70, 70, 90, 70, 70], 100)

    sleep(3)

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回: {response}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际类型 {type(response)}"

    with allure.step("断言返回值与预期相等"):
        assert response == case["expect_data"], f"期望 {case['expect_data']}，实际 {response}"

@allure.feature("夹爪状态接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 3], ids=lambda c: c["title"])
def test_get_gripper_status_3(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameters:{case["parameter"]}')

    print("请取下夹爪夹取的物体后，按 Enter 继续...")
    input()

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回: {response}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际类型 {type(response)}"

    with allure.step("断言返回值与预期相等"):
        assert response == case["expect_data"], f"期望 {case['expect_data']}，实际 {response}"

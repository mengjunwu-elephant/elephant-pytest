import pytest
import allure
from time import sleep
from common1 import logger
from settings import ProGripperBase
from common1.test_data_handler import get_test_data_from_excel

# 获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "get_gripper_status")

@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 0], ids=lambda c: c["title"])
@allure.feature("获取夹爪状态")
@allure.story("夹爪移动状态检测")
def test_get_gripper_status_0(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("设置夹爪移动参数"):
        logger.debug(f'API: {case["api"]}, 参数: {case["parameter"]}')
        device.m.set_gripper_value(100, 5)
        sleep(0.2)

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回结果：{response}")

    with allure.step("断言返回类型和期望值"):
        assert isinstance(response, int), f"类型错误，返回：{type(response)}"
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 1], ids=lambda c: c["title"])
@allure.feature("获取夹爪状态")
@allure.story("夹爪静止状态检测")
def test_get_gripper_status_1(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("等待夹爪静止"):
        logger.debug(f'API: {case["api"]}, 参数: {case["parameter"]}')
        sleep(5)

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回结果：{response}")

    with allure.step("断言返回类型和期望值"):
        assert isinstance(response, int), f"类型错误，返回：{type(response)}"
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 2], ids=lambda c: c["title"])
@allure.feature("获取夹爪状态")
@allure.story("检测夹爪夹持物体状态")
def test_get_gripper_status_2(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("等待用户放置物体后开始测试"):
        input("请放置物体到夹爪中间后，按回车继续")
        device.m.set_gripper_value(0, 100)
        sleep(3)

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回结果：{response}")

    with allure.step("断言返回类型和期望值"):
        assert isinstance(response, int), f"类型错误，返回：{type(response)}"
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 3], ids=lambda c: c["title"])
@allure.feature("获取夹爪状态")
@allure.story("检测夹爪已松开物体状态")
def test_get_gripper_status_3(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("等待用户取下物体后开始测试"):
        input("请取下夹爪夹取的物体后，按回车继续")

    with allure.step("获取夹爪状态"):
        response = device.m.get_gripper_status()
        logger.debug(f"接口返回结果：{response}")

    with allure.step("断言返回类型和期望值"):
        assert isinstance(response, int), f"类型错误，返回：{type(response)}"
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"

    logger.info(f'✅ 用例【{case["title"]}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


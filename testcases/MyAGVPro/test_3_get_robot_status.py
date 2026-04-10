import time
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "get_robot_status")

@pytest.fixture(autouse=True)
def reset(device):
    # 每个用例后自动上电
    yield
    device.mc.power_on()

@allure.feature("读取机器状态")
@allure.story("上下电读取机器状态")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_robot_status1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    if case['ID'] == 1:
        with allure.step("机械臂上电"):
            device.mc.power_on()
    elif case['ID'] == 2:
        with allure.step("机械臂下电"):
            device.mc.power_off()
            time.sleep(1)

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 get_robot_status 接口"):
        response = device.mc.get_robot_status()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 tuple"):
        assert isinstance(response, tuple), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == eval(expected), f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("读取机器状态")
@allure.story("异常读取机器状态")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_get_robot_status2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    if case['ID'] == 3:
        input(f'请拍下急停')
    elif case['ID'] == 4:
        input(f'请触发防撞条1')
    elif case['ID'] == 5:
        input(f'请触发防撞条2')

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 get_robot_status 接口"):
        response = device.mc.get_robot_status()
        logger.debug(f"接口返回：{response}")

    if case['ID'] == 3:
        input(f'请松开急停')

    with allure.step("断言返回值类型为 tuple"):
        assert isinstance(response, tuple), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == eval(expected), f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("读取机器状态")
@allure.story("断开电机读取机器状态")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "Disconnect"], ids=lambda c: c["title"])
def test_get_robot_status3(device, case):
    title = case["title"]
    expected = case["expect_data"]

    input(f"请断开电机{case['ID'] - 5}连接, 其他电机正常连接")
    device.reset()

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 get_robot_status 接口"):
        response = device.mc.get_robot_status()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 tuple"):
        assert isinstance(response, tuple), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == eval(expected), f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

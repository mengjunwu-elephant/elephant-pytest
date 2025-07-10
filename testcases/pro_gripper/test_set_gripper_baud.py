import pytest
import allure
from time import sleep

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_gripper_baud")
baud_map = {0: 115200, 1: 1000000, 2: 57600, 3: 19200, 4: 9600, 5: 4800}


@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 恢复默认波特率为115200
    dev = ProGripperBase(baudrate=1000000)
    dev.m.set_gripper_baud(0)
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪波特率")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_baud(device, case):
    title = case["title"]
    param = int(case["parameter"])
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f"test_api: {case['api']}")
        logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("调用接口 set_gripper_baud 设置波特率"):
        set_res = device.m.set_gripper_baud(param)
        logger.debug(f"设置波特率返回：{set_res}")

    with allure.step("重连夹爪以验证波特率是否设置成功"):
        device.m.close()
        sleep(0.5)
        reconnect_device = ProGripperBase(baudrate=baud_map.get(param))
        sleep(1)
        get_res = reconnect_device.m.get_gripper_baud()
        logger.debug(f"读取波特率返回：{get_res}")

    with allure.step("断言返回类型和波特率是否设置成功"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"
        assert set_res == case["expect_data"], f"设置返回值不一致，期望 {case['expect_data']}，实际为 {set_res}"
        assert get_res == param, f"波特率读取不一致，期望 {param}，实际为 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪波特率")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_baud_invalid(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f"test_api: {case['api']}")
        logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("尝试设置非法波特率并捕获异常"):
        with pytest.raises(ValueError, match=".*"):
            device.m.set_gripper_baud(int(case["parameter"]))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_baud")

baud = {0: 115200, 1: 1000000, 2: 57600, 3: 19200, 4: 9600, 5: 4800}

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 恢复默认波特率并关闭连接
    dev = MyHandBase(baudrate=1000000)
    dev.m.set_gripper_baud(0)
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪波特率")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])
def test_set_gripper_baud(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_parameters:{case["parameter"]}')

    set_res = device.m.set_gripper_baud(case["parameter"])
    device.m.close()
    # 重新实例化device，更新波特率
    new_device = MyHandBase(baudrate=baud[case["parameter"]])
    get_res = new_device.m.get_gripper_baud()

    assert isinstance(set_res, int), f"返回类型断言失败，实际类型为{type(set_res)}"
    assert set_res == case['expect_data'], f"设置返回断言失败，期望：{case['expect_data']}，实际：{set_res}"
    assert get_res == case["parameter"], f"获取波特率断言失败，期望：{case['parameter']}，实际：{get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("设置夹爪波特率")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_baud_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_parameters:{case["parameter"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 parameter={case['parameter']}"):
        with pytest.raises(ValueError, match=".*"):
            device.m.set_gripper_baud(int(case['parameter']))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

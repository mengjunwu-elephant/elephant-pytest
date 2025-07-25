from time import sleep

import pytest
import allure
from common1 import logger
from common1.etest_data_handler import get_test_data_from_excel
from settings import *

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "clear_queue")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    # 设置插补模式
    dev.mc.set_fresh_mode(0)
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 设置刷新模式
    dev.mc.go_home()
    dev.mc.set_fresh_mode(1)
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

# @allure.feature("固件版本获取")
@allure.story("清空队列数据")
@pytest.mark.parametrize("case", cases, ids=[case["title"] for case in cases])
def test_get_basic_version(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    # 机械臂回零位
    Mycobot280Base.go_zero(device)
    #控制机械臂依次运行至45，在第3关节运动完后使用clear_queue接口

    for i in range(6):
        device.mc.send_angle(i+1,45,50)
        sleep(0.5)
        if i==4:
            with allure.step("调用 clear_queue 接口"):
                response = device.mc.clear_queue()
                logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
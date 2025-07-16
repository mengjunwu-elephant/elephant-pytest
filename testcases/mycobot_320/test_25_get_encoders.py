import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "get_encoders")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")

    # 机械臂回零
    dev.m.send_angles(dev.angles_init, dev.speed)
    time.sleep(0.5)
    while True:
        if dev.m.is_moving() == 0:
            break
    time.sleep(2)

    yield dev

    # 机械臂回零
    dev.m.send_angles(dev.zero_angles, dev.speed)
    time.sleep(0.5)
    while True:
        if dev.m.is_moving() == 0:
            break
    time.sleep(2)

    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("读取多关节电位值")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_get_encoders1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    device.m.set_encoders(device.zero_encodes, device.speed)
    time.sleep(0.5)
    while True:
        if device.m.is_moving() == 0:
            break
    time.sleep(1)

    with allure.step("调用 get_encoders 接口"):
        response = device.m.get_encoders()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误,应为{type(eval(expected))},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response, eval(expected), tol=30)  # tol代表允许的误差值

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

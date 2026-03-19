import pytest
import allure
from time import sleep

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryBase

# 读取 Excel 测试用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "over_limit_return_zero")

@pytest.fixture(scope="module")
def device():
    """
    初始化和清理设备（机械臂先上电，机械臂后上电；反之下电）
    """
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("超限回零接口")
@allure.story("测试机械臂超限回零功能")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_over_limit_return_zero(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("初始化位置并移动机械臂"):
        device.mc.send_angles(device.coords_init_angles, device.speed)

    with allure.step("发送超限回零指令"):
        response = device.mc.over_limit_return_zero()
        sleep(2)  # 等待运动完成

    with allure.step("获取机械臂当前角度"):
        get_res = device.mc.get_angles()

    with allure.step("机械臂响应类型断言"):
        assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    with allure.step("是否到达位置断言"):
        allure.attach(str(device.init_angles),name='机械臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res),name='机械臂实际值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(device.init_angles),name='机械臂期望值',attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res,device.init_angles,tol=1,name='机械臂超限回零'), f"机械臂未到达初始位置，期望：{device.init_angles}，实际：{get_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

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
    初始化和清理设备（左臂先上电，右臂后上电；反之下电）
    """
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
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
        device.ml.send_angles(device.coords_init_angles, device.speed)
        device.mr.send_angles(device.coords_init_angles, device.speed)

    with allure.step("发送超限回零指令"):
        l_response = device.ml.over_limit_return_zero()
        r_response = device.mr.over_limit_return_zero()
        sleep(2)  # 等待运动完成

    with allure.step("获取机械臂当前角度"):
        l_get_res = device.ml.get_angles()
        r_get_res = device.mr.get_angles()

    with allure.step("响应类型断言"):
        assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

    with allure.step("响应值结果"):
        assert l_response == case['l_expect_data'], f"左臂返回不符，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case['r_expect_data'], f"右臂返回不符，期望：{case['r_expect_data']}，实际：{r_response}"

    with allure.step("是否到达位置断言"):
        allure.attach(str(device.init_angles),name='左臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_get_res),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(device.init_angles),name='右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_get_res),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(l_get_res,device.init_angles,tol=1,name='左臂超限回零'), f"左臂未到达初始位置，期望：{device.init_angles}，实际：{l_get_res}"
        assert_almost_equal(r_get_res,device.init_angles,tol=1,name='右臂超限回零'), f"右臂未到达初始位置，期望：{device.init_angles}，实际：{r_get_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

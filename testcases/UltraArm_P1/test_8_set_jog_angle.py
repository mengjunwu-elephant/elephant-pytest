import time
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_jog_angle")


@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.go_zero()

@allure.feature("点动控制关节")
@allure.story("设置set_jog_angle")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_jog_angle0(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'position:{case["position"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_jog_angle(case["joint"],case["position"],case["speed"])
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f'调用 get_angles 接口'):
        get_res = device.mc.get_angles_info()[case["joint"]-1]
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(set_res, str), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言 get_angles 返回值"):
        allure.attach(str(case["target_angle"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, case["target_angle"], 1,'设置set_jog_angle'), f"用例【{title}】断言失败，期望 {case['target_angle']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("点动控制关节")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_jog_angle_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'position:{case["position"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"断言抛出 ultraArmP1DataException,关节为{case['joint']},方向为{case['position']}, 速度为{case['speed']}"):
        with pytest.raises(ultraArmP1DataException):
            device.mc.set_jog_angle(case["joint"],case["position"], case["speed"])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

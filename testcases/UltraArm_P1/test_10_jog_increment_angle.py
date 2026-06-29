import time
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "jog_increment_angle")


@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.go_zero()
    device.wait()

@allure.feature("关节步进模式")
@allure.story("正确设置jog_increment_angle")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_jog_increment_angle0(device, case):
    title = case["title"]
    expected = case["expect_data"]
    joint = case["joint"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'increment:{case["increment"]}')
    logger.debug(f'speed:{case["speed"]}')
    logger.debug(f'target_angle:{case["target_angle"]}')

    with allure.step(f"调整关节角度，避免耦合"):
        if joint == 2:
            device.mc.set_angle(3,120,device.speed)
            device.wait()
        elif joint == 3:
            device.mc.set_angle(2,50,device.speed)
            device.wait()
        elif joint == 3 and case["increment"] == -30:
            device.mc.set_angle(3,150,device.speed)
            device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.jog_increment_angle(case["joint"],case["increment"],case["speed"])
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f'调用 get_angle 接口'):
        get_res = device.mc.get_angles_info()[case["joint"]-1]
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(set_res, str), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言 get_angle 返回值"):
        allure.attach(str(case["target_angle"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, case["target_angle"], 1,'正确设置jog_increment_angle'), f"用例【{title}】断言失败，期望 {case['target_angle']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("点动控制关节")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_jog_increment_angle_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'increment:{case["increment"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"断言抛出 ultraArmP1DataException,关节为{case['joint']},增量为{case['increment']}, 速度为{case['speed']}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.jog_increment_angle(case["joint"],case["increment"], case["speed"])

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

import time
import pytest
import allure
from pymycobot.error import MercuryE1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryE1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MercuryE1Base.TEST_DATA_FILE, "set_collision_mode")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = MercuryE1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.wait()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置碰撞检测模式")
@allure.story("正确设置碰撞检测模式")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_collision_mode1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'mode:{case["mode"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_collision_mode(case['mode'])
        logger.debug(f"接口返回：{set_res}")

    with allure.step('调用 get_collision_mode 接口'):
        get_res = device.mc.get_collision_mode()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言碰撞检测是否设置成功"):
        allure.attach(str(case['mode']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert case['mode'] == get_res, f"用例【{title}】断言失败，期望 {case['coords']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置碰撞检测模式")
@allure.story("查看碰撞检测模式是否可触发")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "logic"], ids=lambda c: c["title"])
def test_set_collision_mode2(device, case):
    title = case["title"]
    expected = eval(case["expect_data"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'mode:{case["mode"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_collision_mode(case['mode'])
        logger.debug(f"接口返回：{set_res}")

    with allure.step('提示即将进行碰撞检测'):
        input('即将进行碰撞检测，请手动阻止机械臂运动')

    with allure.step('使机械臂运动到初始姿态'):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step('调用 get_error_information 接口'):
        get_res = device.mc.get_error_information()
        logger.debug(f"接口返回：{get_res}")

    with allure.step("提示观察触发碰撞检测后末端颜色"):
        res =input('观察触发碰撞检测后末端颜色是否为红色，不为红色输入0')
        if res == '0':
            assert False, "碰撞检测未触发"

    with allure.step("碰撞测试完成恢复运动"):
        device.mc.resume()

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res in expected, f"用例【{title}】断言失败，期望 {expected},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


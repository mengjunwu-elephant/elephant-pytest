import time
import pytest
import allure
from pymycobot.error import MyCobot280DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "send_coords")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置全关节坐标")
@allure.story("插补模式设置全坐标")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_send_coords0(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'coords:{case["coords"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f'设置为插补模式'):
        device.mc.set_fresh_mode(0)
        mode = '刷新' if device.mc.get_fresh_mode() else '插补'
        logger.debug(f'当前模式为{mode}')

    with allure.step("使机械臂运动到坐标初始姿态"):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.send_coords(eval(case["coords"]),case["speed"])
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f'调用 get_coords 接口'):
        get_res = device.mc.get_coords()
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言 get_coords 返回值"):
        allure.attach(str(case["coords"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, eval(case["coords"]), 5,'插补模式设置全坐标'), f"用例【{title}】断言失败，期望 {case['coords']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置全关节坐标")
@allure.story("刷新模式设置全坐标")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal1"], ids=lambda c: c["title"])
def test_send_coords1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'coords:{case["coords"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f'设置为刷新模式'):
        device.mc.set_fresh_mode(1)
        mode = '刷新' if device.mc.get_fresh_mode() else '插补'
        logger.debug(f'当前模式为{mode}')

    with allure.step("使机械臂运动到坐标初始姿态"):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.send_coords(eval(case["coords"]), case["speed"])
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f'调用 get_coords 接口'):
        get_res = device.mc.get_coords()
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言 get_coords 返回值"):
        allure.attach(str(case["coords"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, eval(case["coords"]), 5,
                            '刷新模式设置全坐标'), f"用例【{title}】断言失败，期望 {case['coords']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置全关节坐标")
@allure.story("超限报错验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_coords_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'coords:{case["coords"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"断言抛出 Mycobot280Exception,角度为{case['coords']}, 速度为{case['speed']}"):
        with pytest.raises(MyCobot280DataException):
            device.mc.send_coords(eval(case["coords"]), case["speed"])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
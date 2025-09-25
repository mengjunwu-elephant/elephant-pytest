import time
import pytest
import allure
from pymycobot.error import MyCobot280DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "get_coords_plan")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def go_zero(device):
    device.mc.go_home()
    device.wait()

@allure.feature("获取坐标规划值")
@allure.story("插补模式坐标规划值")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_coords_plan0(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f'设置为插补模式'):
        device.mc.set_fresh_mode(0)
        mode = '刷新' if device.mc.get_fresh_mode() else '插补'
        logger.debug(f'当前模式为{mode}')

    with allure.step('使机械臂进行全关节运行'):
        set_res = device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        get_res = device.mc.get_coords_plan()
        logger.debug(f"接口返回：{get_res}")

    with allure.step(f'调用 send_angles 接口'):
        device.mc.send_coords(get_res, device.speed)
        device.wait()

    with allure.step("人工判断关节是否有下坠现象"):
        result = input("请判断关节是否有下坠现象，有下坠现象输入0，按回车键继续")
        if result == '0':
            assert False, f"用例{case['title']}测试失败，关节存在下坠"

    with allure.step("断言返回值类型为 list"):
        assert isinstance(get_res, list), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, eval(expected),2,'获取关节坐标规划值') , f"用例【{title}】断言失败，期望 {expected},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("获取角度规划值")
@allure.story("刷新模式角度规划值")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal1"], ids=lambda c: c["title"])
def test_get_coords_plan1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')


    with allure.step(f'设置为刷新模式'):
        device.mc.set_fresh_mode(1)
        mode = '刷新' if device.mc.get_fresh_mode() else '插补'
        logger.debug(f'当前模式为{mode}')

    with allure.step('使机械臂进行全关节运行'):
        set_res = device.mc.send_angles(device.coords_init_angles, device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        get_res = device.mc.get_coords_plan()
        logger.debug(f"接口返回：{get_res}")

    with allure.step(f'调用 send_coords 接口'):
        device.mc.send_coords(get_res, device.speed)
        device.wait()

    with allure.step("人工判断关节是否有下坠现象"):
        result = input("请判断关节是否有下坠现象，有下坠现象输入0，按回车键继续")
        if result == '0':
            assert False, f"用例{case['title']}测试失败，关节存在下坠"

    with allure.step("断言返回值类型为 list"):
        assert isinstance(get_res, list), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, eval(expected), 2,
                            '获取关节坐标规划值'), f"用例【{title}】断言失败，期望 {expected},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import Mycobot450Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "set_tool_reference")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_tool_reference()
    dev.go_zero()
    dev.wait()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置工具坐标系")
@allure.story("正确设置工具坐标系")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_tool_reference1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"使机械臂运动到坐标初始姿态"):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step('读取设置工具坐标系前坐标'):
        if case['axis'] == 1:
            init_coord = device.mc.get_coords()[1]
        elif case['axis'] == 2:
            init_coord = device.mc.get_coords()[2]
        elif case['axis'] == 3:
            init_coord = device.mc.get_coords()[0]
        elif case['axis'] == 4:
            init_coord = device.mc.get_coords()[4]
        elif case['axis'] == 5:
            init_coord = device.mc.get_coords()[0]

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_tool_reference(eval(case["coords"]))
        logger.debug(f"接口返回：{set_res}")

    with allure.step('调用 set_end_type 接口'):
        device.mc.set_end_type(1)

    with allure.step('调用 get_tool_reference 接口'):
        get_res = device.mc.get_tool_reference()
        logger.debug(f"接口返回：{get_res}")

    with allure.step('调用 get_coords 接口,查看工具坐标系是否设置成功'):
        target_coord = device.mc.get_coords()[case['axis']-1]
        if case['axis'] in [1,2]:
            init_coord = init_coord + 50
        elif case['axis'] in [3,4]:
            init_coord = init_coord - 50

    with allure.step("查看机械臂运动状态，判断工具坐标系是否设置成功"):
        logger.debug(f"即将进行{case['axis']}轴jog_rpy运动,请观察机械臂运动姿态")
        device.mc.jog_rpy(case['axis'], 1,device.speed)
        result = input(f'已修改{case["axis"]}轴坐标，请检查机械臂运动姿态，测试失败输入0')
        if result == '0':
            assert False, f"用例【{title}】测试失败，期望 {init_coord},实际 {target_coord}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言工具坐标系是否设置成功"):
        allure.attach(str(init_coord), name="初始坐标", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(target_coord), name="目标坐标", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(init_coord,target_coord,0.1,'设置工具坐标系'), f"用例【{title}】断言失败，期望 {init_coord},实际 {target_coord}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


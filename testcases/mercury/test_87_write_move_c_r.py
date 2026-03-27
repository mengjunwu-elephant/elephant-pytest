import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase
from time import sleep

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "write_move_c_r")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = MercuryBase()
    dev.power_on()
    dev.go_zero()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.power_off()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("圆弧轨迹运动")
@allure.story("正确设置圆弧轨迹运动")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_write_move_c_r1(device, case):
    title = case["title"]
    expected = case["l_expect_data"]
    coords = eval(case["coords"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"机械臂运动到圆弧起始点"):
        device.mc.send_angles(device.coords_init_angles, device.speed)
        device.mc.send_angle(1,10,device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.write_move_c_r(coords,case["r"],case["speed"],case["rank"])
        sleep(1)
        get_res = device.mc.get_coords()
        logger.debug(f"接口返回：{response},get_res返回：{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    with allure.step('断言 get_coords 接口返回值是否匹配预期'):
        allure.attach(str(coords), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(coords), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(coords,get_res,tol=3,name='机械臂发送全坐标'), f"机械臂响应不一致，期望: {coords}，实际: {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("圆弧轨迹运动")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_write_move_c_r_exception(device, case):
    title = case["title"]
    expected = case["l_expect_data"]
    coords = eval(case["coords"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.mc.write_move_c_r(coords,case["r"],case["speed"],case["rank"])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("圆弧轨迹运动")
@allure.story("仅上电调用")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    expected = case["l_expect_data"]
    coords = eval(case["coords"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.write_move_c_r(coords,case["r"],case["speed"],case["rank"])
        sleep(1)
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert expected == response, f"机械臂响应不一致，期望: {expected}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("圆弧轨迹运动")
@allure.story("下电调用")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    expected = case["l_expect_data"]
    coords = eval(case["coords"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.write_move_c_r(coords,case["r"],case["speed"],case["rank"])
        sleep(1)
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert expected == response, f"机械臂响应不一致，期望: {expected}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

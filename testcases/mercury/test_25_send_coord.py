import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_coord")

@pytest.fixture(scope="module")
def device():
    """初始化设备，仅模块级一次"""
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("设备初始化完成")
    yield dev
    dev.mc.power_on()
    dev.go_zero()
    dev.mc.power_off()
    dev.close()
    logger.info("设备已关闭")

@pytest.fixture(autouse=True)
def reset_coords(device):
    """每个用例前初始化坐标"""
    device.init_coords()

@allure.feature("设置单坐标")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_coord_normal(device, case):
    allure.dynamic.title(case["title"])
    logger.info(f"【开始测试】：{case['title']}")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    with allure.step("机械臂发送坐标"):
        resp = device.mc.send_coord(axis, param, speed)
        device.wait()
        logger.debug(f"机械臂返回：{resp}")

    with allure.step("机械臂发送坐标"):
        r_resp = device.mc.send_coord(axis, param, speed)
        device.wait()
        logger.debug(f"机械臂返回：{r_resp}")

    with allure.step('获取单坐标'):
        get_res = device.mc.get_coords()[axis-1]

    with allure.step('断言返回类型'):
        assert isinstance(resp, int), f"机械臂返回类型错误，应为 int，实际为 {type(resp)}"
        assert resp == case["l_expect_data"], f"机械臂预期 {case['l_expect_data']}，实际 {resp}"
        assert isinstance(r_resp, int), f"机械臂返回类型错误，应为 int，实际为 {type(r_resp)}"

    with allure.step('断言 get_coords 接口返回值是否匹配预期'):
        allure.attach(str(param), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(param), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res,param,tol=3,name='机械臂发送单坐标'), f"机械臂响应不一致，期望: {param}，实际: {get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置单坐标")
@allure.story("异常用例 - 机械臂")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_coord_exception(device, case):
    allure.dynamic.title(f"[机械臂异常] {case['title']}")
    logger.info(f"【开始测试 - 机械臂异常】：{case['title']}")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    with allure.step("发送非法坐标参数至机械臂"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.send_coord(axis, param, speed)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"✅ 机械臂异常用例【{case['title']}】验证通过")

@allure.feature("设置单坐标")
@allure.story("仅上电设置单坐标")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    logger.debug(f'test_api: {case["api"]}')

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("机械臂设置单坐标"):
        response = device.mc.send_coord(axis, param, speed)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置单坐标")
@allure.story("下电设置单坐标")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    logger.debug(f'test_api: {case["api"]}')

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("机械臂设置单坐标"):
        response = device.mc.send_coord(axis, param, speed)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置单坐标")
@allure.story("异常用例 - 奇异点")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "logic"], ids=lambda c: c["title"])
def test_send_coord_exception_1(device, case):
    allure.dynamic.title(f"[机械臂异常] {case['title']}")
    logger.info(f"【开始测试 - 机械臂异常】：{case['title']}")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    #控制机械臂运动到奇异点
    device.mc.power_on()
    device.mc.send_angles([3.215, 43.768, -1.043, -3.046, -0.085, 178.229, -0.011],speed)
    device.wait()

    with allure.step("机械臂发送坐标"):
        r_resp = device.mc.send_coord(axis, param, speed)
        device.wait()
        logger.debug(f"机械臂返回：{r_resp}")

    if case['ID'] == 25:
        ret = input('查看末端有无变蓝，变蓝输入1，未变蓝输入其他')

        with allure.step('断言末端有无变蓝'):
            assert ret == '1' , f"机械臂未变蓝，预期 1，实际 {ret}"

    with allure.step('断言返回类型'):
        assert r_resp == case["l_expect_data"], f"机械臂预期 {case['l_expect_data']}，实际 {r_resp}"
        assert isinstance(r_resp, int), f"机械臂返回类型错误，应为 int，实际为 {type(r_resp)}"
    #清除报错
    device.mc.clear_error_information()

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
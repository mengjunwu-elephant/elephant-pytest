import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_coords")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def init_coords(device):
    device.init_coords()

@allure.feature("设置全坐标")
@allure.story("正常路径测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_coords(device, case):
    allure.dynamic.title(case["title"])
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")

    param = eval(case["parameter"])
    speed = case["speed"]

    with allure.step("机械臂发送坐标"):
        response = device.mc.send_coords(param, speed)
        device.wait()
        logger.debug(f"机械臂返回值：{response}")

    with allure.step("获取机械臂坐标"):
        get_res = device.mc.get_coords()
        logger.debug(f"机械臂获取坐标：{get_res}")

    with allure.step('断言返回类型'):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"
        assert response == case["l_expect_data"], f"机械臂期望值：{case['l_expect_data']}，实际值：{response}"

    with allure.step('断言 get_coords 接口返回值是否匹配预期'):
        allure.attach(str(param), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(param), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res,param,tol=3,name='机械臂发送全坐标'), f"机械臂响应不一致，期望: {param}，实际: {get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("send_coords 接口测试")
@allure.story("机械臂边界与异常用例")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c.get("test_type") in {"exception", "left", "right"}],
    ids=lambda c: c["title"],
)
def test_send_coords_out_limit(device, case):
    allure.dynamic.title(f"[机械臂] {case['title']}")
    param = eval(case["parameter"])
    speed = case["speed"]

    logger.info(f"》》》》》用例【{case['title']}】开始测试（机械臂）《《《《《")
    with allure.step("机械臂发送非法坐标，断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.send_coords(param, speed)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"✅ 用例【{case['title']}】机械臂异常验证成功")

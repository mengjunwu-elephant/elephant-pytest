import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_base_coord")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.mark.parametrize(
    "case",
    [c for c in cases if c.get("test_type") in ("left", "right")],
    ids=lambda c: c["title"],
)
@allure.feature("发送基础单轴坐标")
@allure.story("机械臂正常用例")
def test_send_base_coord(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        device.init_coords()
        logger.debug(f"API: {case['api']}, 轴: {case['axis']}, 参数: {case['parameter']}, 速度: {case['speed']}")

        with allure.step("调用机械臂 send_base_coord"):
            response = device.mc.send_base_coord(case["axis"], case["parameter"], case["speed"])
            logger.debug(f"机械臂响应: {response}")

        with allure.step("断言返回类型为int"):
            assert isinstance(response, int), f"机械臂返回类型错误，实际类型: {type(response)}"

        with allure.step("断言返回值与期望相等"):
            assert response == case['l_expect_data'], f"机械臂期望={case['l_expect_data']}，实际={response}"

        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("发送基础单轴坐标")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_base_coord_exception(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        device.init_coords()
        logger.debug(f"API: {case['api']}, 轴: {case['axis']}, 参数: {case['parameter']}, 速度: {case['speed']}")

        with allure.step("调用机械臂 send_base_coord 并期望抛出 MercuryDataException"):
            with pytest.raises(MercuryDataException) as exc_info:
                device.mc.send_base_coord(case["axis"], case["parameter"], case["speed"])

        logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
        logger.info(f"》》》用例【{title}】测试完成《《《")

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从 Excel 中加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_color")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置颜色")
@allure.story("正常用例 - 设置机械臂颜色")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c.get("test_type") == "normal"],
    ids=lambda c: c["title"],
)
def test_set_color_normal(device, case):
    title = case["title"]
    r, g, b = case["r"], case["g"], case["b"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: set_color, 参数: r={r}, g={g}, b={b}")

    with allure.step("机械臂发送设置颜色指令"):
        response = device.mc.set_color(r, g, b)
    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"

    with allure.step("断言返回值正确"):
        assert response == case["l_expect_data"], f"机械臂期望={case['l_expect_data']}, 实际={response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置颜色")
@allure.story("异常用例 - 设置颜色参数越界抛异常")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c.get("test_type") == "exception"],
    ids=lambda c: c["title"],
)
def test_set_color_exception(device, case):
    title = case["title"]
    r, g, b = case["r"], case["g"], case["b"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: set_color, 参数: r={r}, g={g}, b={b}")

    with allure.step("断言设置非法颜色值抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_color(r, g, b)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

import time

import pytest
import allure
from pymycobot.error import MercuryDataException, MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从 Excel 中加载用例
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "set_color")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_color(0,255,0)
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置颜色")
@allure.story("正常用例 - 设置颜色")
@pytest.mark.parametrize("case",[c for c in cases if c.get("test_type") == "normal"],ids=lambda c: c["title"])
def test_set_color_normal(device, case):
    title = case["title"]
    r, g, b = case["r"], case["g"], case["b"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: set_color, 参数: r={r}, g={g}, b={b}")

    with allure.step('目测末端颜色变化'):
        input('正在进行末端颜色测试，请确认末端颜色变化依次设置为红绿蓝，按回车键继续')

    with allure.step("发送设置颜色指令"):
        response = device.mc.set_color(r, g, b)
        time.sleep(2)

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误：{type(response)}"

    with allure.step("断言返回值正确"):
        assert response == case["expect_data"], f"期望={case['expect_data']}, 实际={response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置颜色")
@allure.story("异常用例 - 设置颜色参数越界抛异常")
@pytest.mark.parametrize("case",[c for c in cases if c.get("test_type") == "exception"],ids=lambda c: c["title"])
def test_set_color_exception(device, case):
    title = case["title"]
    r, g, b = case["r"], case["g"], case["b"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: set_color, 参数: r={r}, g={g}, b={b}")

    with allure.step("断言设置非法颜色值抛出 MyCobotPro450DataException"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.set_color(r, g, b)

    logger.info(f"✅ 异常断言成功，用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
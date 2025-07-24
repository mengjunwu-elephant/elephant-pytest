import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从 Excel 加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_collision_mode")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置碰撞模式")
@allure.story("正常用例 - 设置左右臂碰撞模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_collision_mode_normal(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试参数: {param}")

    with allure.step("发送设置碰撞模式指令"):
        l_response = device.ml.set_collision_mode(param)
        r_response = device.mr.set_collision_mode(param)

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言返回值正确"):
        assert l_response == case["l_expect_data"], f"左臂期望={case['l_expect_data']}, 实际={l_response}"
        assert r_response == case["r_expect_data"], f"右臂期望={case['r_expect_data']}, 实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置碰撞模式")
@allure.story("异常用例 - 设置非法碰撞模式值应抛出异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_collision_mode_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试参数: {param}")

    with allure.step("断言设置非法碰撞模式值抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.set_collision_mode(param)
        with pytest.raises(MercuryDataException):
            device.mr.set_collision_mode(param)

    logger.info(f"✅ 异常断言成功，用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

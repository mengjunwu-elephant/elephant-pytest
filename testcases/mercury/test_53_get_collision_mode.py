import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从 Excel 中提取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_collision_mode")


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


@allure.feature("获取碰撞模式")
@allure.story("正常用例 - 获取左右臂碰撞模式并验证返回值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_collision_mode(device, case):
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("获取左臂和右臂的碰撞模式"):
        l_response = device.ml.get_collision_mode()
        r_response = device.mr.get_collision_mode()

    with allure.step("断言返回类型正确"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        logger.debug("左臂请求类型断言成功")
        logger.debug("右臂请求类型断言成功")

    with allure.step("断言返回值与期望值一致"):
        assert l_response == case['l_expect_data'], f"左臂返回值错误：期望={case['l_expect_data']}, 实际={l_response}"
        assert r_response == case['r_expect_data'], f"右臂返回值错误：期望={case['r_expect_data']}, 实际={r_response}"
        logger.info(f"✅ 用例【{title}】测试通过")

    logger.info(f"》》》用例【{title}】测试完成《《《")

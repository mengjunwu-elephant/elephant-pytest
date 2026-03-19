import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从 Excel 中加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_collision_threshold")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("碰撞阈值接口")
@allure.story("获取碰撞阈值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_collision_threshold(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"用例信息: {case}")

    # 请求发送
    response = device.mc.get_collision_threshold()

    # 类型断言
    assert isinstance(response, list), f"机械臂返回类型应为 list，实际为 {type(response)}"

    # 数据断言
    expected = eval(case["l_expect_data"])

    assert response == expected, f"机械臂期望值: {expected}, 实际值: {response}"

    logger.info(f"✅ 用例【{title}】测试成功")

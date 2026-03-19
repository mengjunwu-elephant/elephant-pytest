import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_joint_min_angle")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def restore_zero(device):
    # 每个测试用例后恢复零点
    yield
    device.go_zero()
    device.wait()

@allure.feature("获取关节最小角度")
@allure.story("正常用例 - 可达性与返回值验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_joint_min_angle_normal(device, case):
    title = case["title"]
    joint_id = case["id"]
    l_expect = case["l_expect_data"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("获取机械臂最小角度"):
        response = device.mc.get_joint_min_angle(joint_id)
        logger.info(f"机械臂最小角度：{response}")

    with allure.step("返回值断言"):
        assert isinstance(response, float), f"机械臂返回类型错误：{type(response)}"
        assert response == l_expect, f"机械臂最小角断言失败：预期={l_expect}, 实际={response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取关节最小角度")
@allure.story("异常用例 - 参数越界验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_joint_min_angle_exception(device, case):
    title = case["title"]
    joint_id = case["id"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.get_joint_min_angle(joint_id)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

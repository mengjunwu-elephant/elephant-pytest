import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取 Excel 测试用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_solution_angles")


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


@allure.feature("解算角度接口")
@allure.story("获取机械臂解算角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_solution_angles(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Parameter: {case['parameter']}")

    with allure.step("调用 get_solution_angles 接口"):
        l_response = device.ml.get_solution_angles()
        r_response = device.mr.get_solution_angles()

    with allure.step("断言返回类型"):
        assert isinstance(l_response, float), f"左臂返回类型应为 float，实际为 {type(l_response)}"
        assert isinstance(r_response, float), f"右臂返回类型应为 float，实际为 {type(r_response)}"

    with allure.step("断言返回值"):
        assert l_response == case["l_expect_data"], f"左臂返回值不符，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case["r_expect_data"], f"右臂返回值不符，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

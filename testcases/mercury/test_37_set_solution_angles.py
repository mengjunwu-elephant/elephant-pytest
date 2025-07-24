import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_solution_angles")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_position(device):
    yield
    device.init_coords()


@allure.feature("解算角度设置")
@allure.story("正常设置")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_solution_angles_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}, 速度: {case['speed']}")

    with allure.step("发送 set_solution_angles 指令"):
        l_response = device.ml.set_solution_angles(case["parameter"], case["speed"])
        r_response = device.mr.set_solution_angles(case["parameter"], case["speed"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

    with allure.step("断言返回值是否正确"):
        assert l_response == case["l_expect_data"], f"左臂返回值不匹配，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case["r_expect_data"], f"右臂返回值不匹配，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("解算角度设置")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_solution_angles_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}, 速度: {case['speed']}")

    with allure.step("发送非法参数，断言抛出异常"):
        with pytest.raises(MercuryDataException):
            device.ml.set_solution_angles(case["parameter"], case["speed"])
            device.mr.set_solution_angles(case["parameter"], case["speed"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

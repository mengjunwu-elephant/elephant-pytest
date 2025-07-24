import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "power_on")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_off()
    dev.mr.power_off()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("机械臂上电")
@allure.story("正常上电流程")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_power_on_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    device.power_off()

    input(print("请确认末端颜色是否变绿，按回车键继续测试"))

    with allure.step("左臂执行上电"):
        l_response = device.ml.power_on()

    with allure.step("右臂执行上电"):
        r_response = device.mr.power_on()

    with allure.step("断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name= "左臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case["r_expect_data"]),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name= "右臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("机械臂上电")
@allure.story("急停异常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_power_on_emergency(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    input(print("请拍下急停，按回车键继续测试"))

    with allure.step("左臂执行上电"):
        l_response = device.ml.power_on()

    with allure.step("右臂执行上电"):
        r_response = device.mr.power_on()

    input(print("请松开急停，按回车键继续测试"))

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name= "左臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case["r_expect_data"]),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name= "右臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

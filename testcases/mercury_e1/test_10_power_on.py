import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryE1Base

cases = get_test_data_from_excel(MercuryE1Base.TEST_DATA_FILE, "power_on")

@pytest.fixture(scope="module")
def device():
    dev = MercuryE1Base()
    input(print(f'请注意即将放松机械臂，按回车键继续测试'))
    dev.mc.power_off()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_on()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("机械臂上电")
@allure.story("正常上电流程")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_power_on_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("执行上电指令"):
        response = device.mc.power_on()

    with allure.step("判断上电末端颜色是否变绿"):
        result = input(print("请观察上电末端颜色是否变绿，变绿输入1未变绿输入0，按回车键继续测试"))
        assert result == '1', f"断言失败，上电末端颜色未变绿"


    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"左臂返回类型错误：{type(response)}"

    with allure.step("断言返回结果"):
        allure.attach(str(case["expect_data"]),name= "期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"右臂结果断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("机械臂上电")
@allure.story("急停异常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_power_on_emergency(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    input(print("请拍下急停，按回车键继续测试"))

    with allure.step("执行上电指令"):
        response = device.mc.power_on()

    input(print("请松开急停，按回车键继续测试"))

    with allure.step("断言返回结果"):
        allure.attach(str(case["expect_data"]),name= "期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
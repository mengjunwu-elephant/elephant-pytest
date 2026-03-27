import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "power_off")

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
def reset_device(device):
    yield
    device.reset()

@allure.feature("机械臂下电")
@allure.story("正常下电流程")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_power_off_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameter:{case["parameter"]}')

    input(print("请确认末端显示是否关闭，按回车键继续测试"))
    with allure.step("机械臂执行下电"):
        response = device.mc.power_off()

    with allure.step("机械臂断言返回类型"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂结果断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂下电")
@allure.story("急停异常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_power_off_emergency(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameter:{case["parameter"]}')

    input(print("请拍下急停，按回车键继续测试"))

    with allure.step("机械臂执行下电"):
        response = device.mc.power_off()
    input(print("请松开急停，按回车键继续测试"))

    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂结果断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂下电")
@allure.story("仅上电和下电异常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "logic"], ids=lambda c: c["title"])
def test_power_off_normal_1(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameter:{case["parameter"]}')

    if '仅上电时' in title:
        device.mc.power_off()
        device.mc.power_on_only()
    elif '下电时' in title:
        device.mc.power_on()
        device.mc.power_off()

    with allure.step("机械臂执行下电"):
        response = device.mc.power_off()

    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂结果断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
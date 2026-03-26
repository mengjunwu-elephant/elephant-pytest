import time
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE, "set_gripper_enable_status")


@allure.feature("设置夹爪使能状态")
@allure.story("正确设置夹爪使能状态")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_gripper_enable_status(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f'提示请连接夹爪，并确认状态'):
        if case['status'] == '1':
            input("夹爪即将掉使能5s,请确认夹爪使能状态,按回车键继续测试")
        elif case['status'] == '0':
            input("夹爪即将上使能5s,请确认夹爪使能状态,按回车键继续测试")

    with allure.step(f'调用 set_gripper_enable_status 接口'):
        response = device.mc.set_gripper_enable_status(int(case['status']))
        time.sleep(5)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置夹爪使能状态")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_enable_status_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step(f"断言设置接口抛出 ultraArmP1DataException, status: {case['status']}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_gripper_enable_status(case['status'])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功,异常信息：{exc.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
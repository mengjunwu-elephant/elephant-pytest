import pytest
import allure
from pymycobot.error import MercuryRobotException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "power_on_only")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 结束清理顺序
    dev.go_zero()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def power_off_before_each(device):
    device.power_off()
    yield

@allure.feature("机械臂仅上电状态测试")
@allure.story("正常仅上电")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    logger.debug(f"test_api:{case['api']}")
    logger.debug(f"test_parameter:{case['parameter']}")

    input(print("请确认末端颜色是否变黄，按回车键继续测试"))

    with allure.step("机械臂请求发送"):
        response = device.mc.power_on_only()
    with allure.step("机械臂请求结果类型断言"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"
    with allure.step("机械臂请求结果断言"):
        allure.attach(str(case['l_expect_data']),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name='机械臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

@allure.feature("机械臂上电状态测试")
@allure.story("急停测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "emergency"], ids=lambda c: c["title"])
def test_emergency(device, case):
    title = case["title"]
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    logger.debug(f"test_api:{case['api']}")
    logger.debug(f"test_parameter:{case['parameter']}")

    input("请拍下急停，按回车键继续测试")

    with allure.step("机械臂请求发送"):
        response = device.mc.power_on_only()
    input(print("请松开急停，按回车键继续测试"))

    with allure.step("机械臂请求结果类型断言"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂请求结果断言"):
        allure.attach(str(case['l_expect_data']),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name='机械臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

@allure.feature("机械臂上电状态测试")
@allure.story("运动测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "move"], ids=lambda c: c["title"])
def test_move(device, case):
    title = case["title"]
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    logger.debug(f"test_api:{case['api']}")
    logger.debug(f"test_parameter:{case['parameter']}")

    with allure.step("机械臂仅上电"):
        device.mc.power_on_only()
    with allure.step("机械臂仅上电"):
        device.mc.power_on_only()

    with allure.step("机械臂一关节运动十度"):
        move_res_res = device.mc.send_angle(1, 10, device.speed)
    with allure.step("机械臂一关节运动十度"):
        r_move_res = device.mc.send_angle(1, 10, device.speed)

    with allure.step("观察并断言仅上电状态机械臂是否运动"):
        _assert = input("请观察刚刚机械臂是否运动, 如果运动输入1，不运动输入任意数字后回车继续测试")
        if _assert == "1":
            raise AssertionError("仅上电状态不可以控制机械臂运动")

    with allure.step("机械臂请求结果断言"):
        allure.attach(str(case['l_expect_data']),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(move_res_res),name='机械臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert move_res_res == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{move_res_res}"

    with allure.step("机械臂请求结果断言"):
        allure.attach(str(r_move_res),name='机械臂实际值',attachment_type=allure.attachment_type.TEXT)

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

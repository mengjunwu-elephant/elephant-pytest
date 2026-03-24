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
    dev.mr.power_off()
    dev.ml.power_off()
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

    with allure.step("左臂请求发送"):
        l_response = device.ml.power_on_only()
    with allure.step("右臂请求发送"):
        r_response = device.mr.power_on_only()

    with allure.step("左臂请求结果类型断言"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
    with allure.step("右臂请求结果类型断言"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂请求结果断言"):
        allure.attach(str(case['l_expect_data']),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂请求结果断言"):
        allure.attach(str(case['r_expect_data']),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

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

    with allure.step("左臂请求发送"):
        l_response = device.ml.power_on_only()
    with allure.step("右臂请求发送"):
        r_response = device.mr.power_on_only()

    input(print("请松开急停，按回车键继续测试"))

    with allure.step("左臂请求结果类型断言"):
        assert l_response is None, f"左臂返回类型错误，期望None，实际{type(l_response)}"
    with allure.step("右臂请求结果类型断言"):
        assert r_response is None, f"右臂返回类型错误，期望None，实际{type(r_response)}"

    with allure.step("左臂请求结果断言"):
        allure.attach(str(case['l_expect_data']),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂请求结果断言"):
        allure.attach(str(case['r_expect_data']),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

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

    with allure.step("左臂仅上电"):
        device.ml.power_on_only()
    with allure.step("右臂仅上电"):
        device.mr.power_on_only()

    with allure.step("左臂一关节运动十度"):
        l_move_res = device.ml.send_angle(1, 10, device.speed)
    with allure.step("右臂一关节运动十度"):
        r_move_res = device.mr.send_angle(1, 10, device.speed)

    with allure.step("观察并断言仅上电状态机械臂是否运动"):
        _assert = input("请观察刚刚机械臂是否运动, 如果运动输入1，不运动输入任意数字后回车继续测试")
        if _assert == "1":
            raise AssertionError("仅上电状态不可以控制机械臂运动")

    with allure.step("左臂请求结果断言"):
        allure.attach(str(case['l_expect_data']),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_move_res),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_move_res == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_move_res}"

    with allure.step("右臂请求结果断言"):
        allure.attach(str(case['r_expect_data']),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_move_res),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_move_res == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_move_res}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "solve_inv_kinematics")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("逆运动学计算")
@allure.story("正常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_solve_inv_kinematics_normal(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}, {case['parameter_1']}")

        response = device.mc.solve_inv_kinematics(eval(case["parameter"]), eval(case["parameter_1"]))
        logger.info(f'机械臂返回结果{response}')

        with allure.step("断言机械臂返回类型"):
            assert isinstance(response, list), f"机械臂返回类型应为int，实际为：{type(response)}"
        with allure.step("断言机械臂值"):
            assert response == eval(case["l_expect_data"]), f"机械臂期望：{case['l_expect_data']}，实际：{response}"
        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("逆运动学计算-异常场景")
@allure.story("异常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_solve_inv_kinematics_exception(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试（异常分支）"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}, {case['parameter_1']}")

        with allure.step("断言抛出 MercuryDataException"):
            with pytest.raises(MercuryDataException) as exc_info:
                device.mc.solve_inv_kinematics(case["parameter"], case["parameter_1"])
        logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
        logger.info(f"✅ 异常用例【{title}】触发 MercuryDataException 成功")

@allure.feature("逆运动学计算")
@allure.story("仅上电调用 solve_inv_kinematics 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}, {case['parameter_1']}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("获取机械臂逆运动学计算"):
        response = device.mc.solve_inv_kinematics(eval(case["parameter"]), eval(case["parameter_1"]))
        logger.info(f'机械臂返回结果{response}')

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("逆运动学计算")
@allure.story("下电调用 solve_inv_kinematics 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}, {case['parameter_1']}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("获取机械臂逆运动学计算"):
        response = device.mc.solve_inv_kinematics(eval(case["parameter"]), eval(case["parameter_1"]))
        logger.info(f'机械臂返回结果{response}')

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

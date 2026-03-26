import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_model_direction")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    dev.mc.go_home()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
@allure.feature("设置模型方向")
def test_set_model_direction(device, case):
    response = []
    title = case["title"]
    direction = eval(case['direction'])
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"API: {case['api']}")

        with allure.step("改变所有关节运动方向"):
            for i in range(1,8):
                res = device.mc.set_model_direction(i, direction[i - 1])
                response.append(res)
            logger.info(f'机械臂返回结果{response}')

        with allure.step("机械臂运动到[30, 30, 30, 0, 30, 30, 30]"):
            device.mc.send_angles([30, 30, 30, 0, 30, 30, 30], device.speed)

        re = input('机械臂已运动到[30, 30, 30, 0, 30, 30, 30],判断方向是否相反,相反输入1,其他失败')
        with allure.step("断言机械臂运动方向是否正确"):
            assert re == '1', f"机械臂期望：1，实际：{re}，机械臂运动方向有误"

        with allure.step("断言机械臂返回类型为 int"):
            assert isinstance(res, int), f"机械臂返回类型错误，实际为 {type(res)}"
            logger.debug("机械臂请求类型断言成功")

        expected = eval(case['l_expect_data'])

        with allure.step("断言机械臂返回值"):
            assert response == expected, f"机械臂期望：{expected}，实际：{response}"

        device.mc.go_home()
        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置模型方向")
@allure.story("异常用例 - 参数超限")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_model_direction_exception(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"API: {case['api']}")

    with allure.step("断言设置非法参数抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_model_direction(case['joint'], case['direction'])

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置模型方向")
@allure.story("仅上电调用 set_model_direction 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"API: {case['api']}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("设置机械臂模型方向"):
        response = device.mc.set_model_direction(case['joint'], case['direction'])

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

@allure.feature("设置模型方向")
@allure.story("下电调用 set_model_direction 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"API: {case['api']}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("设置机械臂模型方向"):
        response = device.mc.set_model_direction(case['joint'], case['direction'])

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

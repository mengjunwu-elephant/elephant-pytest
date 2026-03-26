import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_pos_over_shoot")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_pos_over_shoot()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("正常用例")
def test_set_pos_over_shoot_normal(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        response = device.mc.set_pos_over_shoot(param)

        with allure.step("断言返回类型为int"):
            assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

        with allure.step("断言返回值符合预期"):
            assert response == case["l_expect_data"], f"机械臂期望: {case['l_expect_data']}，实际: {response}"

        logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("异常用例")
def test_set_pos_over_shoot_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_pos_over_shoot(param)

        logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("位置超调参数设置")
@allure.story("保存与否测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_pos_over_shoot_save_or_not(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        response = device.mc.set_pos_over_shoot(param)

        with allure.step("重启机械臂设备"):
            device.reset()

        with allure.step("获取机械臂的扭矩补偿参数"):
            get_res = device.mc.get_pos_over_shoot()
            logger.debug(f"机械臂当前补偿参数: {get_res}")
        with allure.step("断言响应类型"):
            assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"

        with allure.step("断言实际获取值是否符合预期"):
            expected = case["l_expect_data"]
            assert get_res == expected, f"机械臂期望值: {expected}, 实际值: {get_res}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("位置超调参数设置")
@allure.story("仅上电调用 set_pos_over_shoot 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("调用机械臂 set_pos_over_shoot 接口"):
        response = device.mc.set_pos_over_shoot(param)
        logger.debug(f"机械臂响应: {response}")

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

@allure.feature("位置超调参数设置")
@allure.story("下电调用 set_pos_over_shoot 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("调用机械臂 set_pos_over_shoot 接口"):
        response = device.mc.set_pos_over_shoot(param)
        logger.debug(f"机械臂响应: {response}")

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


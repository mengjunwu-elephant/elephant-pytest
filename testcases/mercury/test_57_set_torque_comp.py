import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_torque_comp")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_torque_comp()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("扭矩补偿接口")
@allure.story("正常设置扭矩补偿")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_torque_comp(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("调用机械臂 set_torque_comp 接口"):
            response = device.mc.set_torque_comp(case["joint"], case["parameter"])
            logger.debug(f"机械臂响应: {response}")
        with allure.step("断言返回值类型"):
            assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"

        with allure.step("断言返回结果是否符合预期"):
            assert response == case["l_expect_data"], f"机械臂期望: {case['l_expect_data']}, 实际: {response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("扭矩补偿接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_torque_comp_exception(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("断言调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException) as exc_info:
                device.mc.set_torque_comp(case["joint"], case["parameter"])

        logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("扭矩补偿接口")
@allure.story("保存与否测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_torque_comp_save_or_not(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("调用机械臂 set_torque_comp 接口"):
            response = device.mc.set_torque_comp(case["joint"], case["parameter"])
            logger.debug(f"机械臂响应: {response}")
        with allure.step("重启机械臂设备"):
            device.reset()

        with allure.step("获取机械臂的扭矩补偿参数"):
            get_res = device.mc.get_torque_comp()
            logger.debug(f"机械臂当前补偿参数: {get_res}")
        with allure.step("断言响应类型"):
            assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"

        with allure.step("断言实际获取值是否符合预期"):
            expected = eval(case["l_expect_data"])
            assert get_res == expected, f"机械臂期望值: {expected}, 实际值: {get_res}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

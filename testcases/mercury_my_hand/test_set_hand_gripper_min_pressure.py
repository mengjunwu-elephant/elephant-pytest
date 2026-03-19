import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_min_pressure")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_mini_pressure()  # 恢复默认最小启动力
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪最小启动力")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_min_pressure_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("发送请求，设置夹爪指定 joint 的最小启动力"):
        set_res = device.mc.set_hand_gripper_min_pressure(case["joint"], case["parameter"])

    with allure.step("获取夹爪指定 joint 的最小启动力"):
        get_res = device.mc.get_hand_gripper_min_pressure(case["joint"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"

    with allure.step("断言设置返回值符合预期"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取的最小启动力值与设置值相同"):
        allure.attach(str(case['parameter']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(get_res),'实际值',allure.attachment_type.TEXT)
        assert get_res == case["parameter"], f"断言失败，期望获取值为 {case['parameter']}，实际为 {get_res}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置夹爪最小启动力")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_min_pressure_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step(f"尝试传入非法参数，预期抛出 MercuryDataException,关节为case['joint'],最小启动力为{case['parameter']}"):
        with pytest.raises(MercuryDataException):
            device.mc.set_hand_gripper_min_pressure(case["joint"], case["parameter"])

    logger.info(f"✅ 用例【{title}】异常断言成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

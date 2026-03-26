import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_torque")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_torque()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪扭矩")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_torque_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("调用设置扭矩接口"):
        set_res = device.ml.set_hand_gripper_torque(case["joint"], case["parameter"])

    with allure.step("调用获取扭矩接口"):
        get_res = device.ml.get_hand_gripper_torque(case["joint"])

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"

    with allure.step("断言设置返回值与预期一致"):
        allure.attach(str(case["expect_data"]),name = '期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res),name = '实际值',attachment_type=allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{set_res}"


    with allure.step("断言获取的扭矩值与设置值一致"):
        allure.attach(str(case["parameter"]),name = '期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res),name = '实际值',attachment_type=allure.attachment_type.TEXT)
        assert get_res == case["parameter"], f"断言失败，期望：{case['parameter']}，实际：{get_res}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置夹爪扭矩")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_torque_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step(f"调用设置扭矩接口并断言异常抛出,关节为{case['joint']},扭矩为{case['parameter']}"):
        with pytest.raises(MercuryDataException) as exc:
            device.ml.set_hand_gripper_torque(case["joint"], case["parameter"])

    logger.info(f"✅ 用例【{title}】异常断言成功,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

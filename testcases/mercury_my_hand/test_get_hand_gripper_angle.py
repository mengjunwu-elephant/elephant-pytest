import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "get_hand_gripper_angle")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.set_hand_gripper_angles([0, 0, 0, 0, 0, 0], dev.speed)
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取单关节角度")
@allure.story("查询单个夹爪角度 - 正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_hand_gripper_angle(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")

    with allure.step("发送请求，获取指定夹爪关节角度"):
        response = device.ml.get_hand_gripper_angle(case["joint"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，期望 int，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case["expect_data"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,case["expect_data"],tol=5,name='读取单关节角度'), f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("获取单关节角度")
@allure.story("查询单个夹爪角度 - 异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_hand_gripper_angle_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_joint: {case['joint']}")

    with allure.step(f"尝试传入异常参数，期望抛出 MercuryDataException,关节为{case['joint']}"):
        with pytest.raises(MercuryDataException) as exc:
            device.ml.get_hand_gripper_angle(case["joint"])

    logger.info(f"✅ 用例【{title}】异常断言成功,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

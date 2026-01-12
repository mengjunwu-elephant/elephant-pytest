import pytest
import allure
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "get_hand_gripper_angles")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.set_hand_gripper_angles([0, 0, 0, 0, 0, 0], dev.speed)
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取全关节角度")
@allure.story("获取所有夹爪关节角度")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_hand_gripper_angles(device, case):
    title = case["title"]
    angles = eval(case['angles'])
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")

    with allure.step('设置全关节角度'):
        device.ml.set_hand_gripper_angles(angles, device.speed)

    with allure.step("发送请求，获取所有夹爪关节角度"):
        response = device.ml.get_hand_gripper_angles()

    with allure.step("断言返回类型为 list"):
        assert isinstance(response, list), f"返回类型错误，期望 list，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        expected = eval(case["expect_data"])
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,expected), f"断言失败，期望：{expected}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

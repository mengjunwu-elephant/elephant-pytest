import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_pose")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 恢复默认状态
    dev.ml.set_hand_gripper_pinch_action_speed_consort(0, 5)
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪捏合动作")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_hand_gripper_pinch_action_speed_consort_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_pose: {case['pose']}")
    logger.debug(f"test_rank: {case['rank']}")
    logger.debug(f"test_is_free: {case['is_free']}")

    with allure.step("发送请求，设置夹爪捏合动作速度协同参数"):
        set_res = device.ml.set_hand_gripper_pinch_action_speed_consort(case["pose"], case["rank"], case["is_free"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"

    with allure.step("断言返回值符合预期"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{set_res}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

    # 等待动作完成，不能小于5秒
    sleep(5)


@allure.feature("设置夹爪捏合动作速度协同参数")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_hand_gripper_pinch_action_speed_consort_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_pose: {case['pose']}")

    with allure.step(f"尝试传入非法参数，预期抛出 MercuryDataException,动作为{case['pose']},范围为{case['rank']},是否自由模式为{case['is_free']}"):
        with pytest.raises(MercuryDataException):
            device.ml.set_hand_gripper_pinch_action_speed_consort(case["pose"], case["rank"], case["is_free"])

    logger.info(f"✅ 用例【{title}】异常断言成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

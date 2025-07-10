import pytest
import allure
import time
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_pose")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_pose(0, 5)  # 恢复默认状态
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("夹爪姿态设置")
@allure.story("正常用例")
@pytest.mark.parametrize("case", cases, ids=[case["title"] for case in cases if case.get("test_type") == "normal"])
def test_set_gripper_pose(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_pose: {case["pose"]}')
    logger.debug(f'test_rank: {case["rank"]}')
    logger.debug(f'test_is_free: {case["is_free"]}')

    with allure.step(f"调用 {case['api']} 接口，参数 pose={case['pose']}, rank={case['rank']}, is_free={case['is_free']}"):
        response = device.m.set_gripper_pose(case["pose"], case["rank"], case["is_free"])
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

    # 模拟 tearDown 中的等待
    time.sleep(5)

@allure.feature("夹爪姿态设置")
@allure.story("异常用例")
@pytest.mark.parametrize("case", cases, ids=[case["title"] for case in cases if case.get("test_type") == "exception"])
def test_set_gripper_pose_exception(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_pose: {case["pose"]}')
    logger.debug(f'test_rank: {case["rank"]}')
    logger.debug(f'test_is_free: {case["is_free"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 pose={case['pose']}, rank={case['rank']}, is_free={case['is_free']}"):
        with pytest.raises(ValueError, match=f".*pose值为{case['pose']}.*"):
            device.m.set_gripper_pose(case["pose"], case["rank"], case["is_free"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

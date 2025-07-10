import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "get_gripper_joint_speed")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("夹爪速度接口")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_gripper_joint_speed_normal(device, case):
    title = case['title']
    joint = case['joint']
    expect = case['expect_data']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_joint:{joint}')

    with allure.step(f"调用接口 get_gripper_joint_speed({joint})"):
        response = device.m.get_gripper_joint_speed(joint)
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，预期 int，实际 {type(response)}"

    with allure.step(f"断言返回结果与期望值相等（期望：{expect}）"):
        allure.attach(str(expect), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expect, f"返回值不匹配，期望 {expect}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("夹爪速度接口")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_gripper_joint_speed_exception(device, case):
    title = case['title']
    joint = case['joint']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_joint:{joint}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 joint={case['joint']}"):
        with pytest.raises(ValueError, match=f".*{joint}.*"):
            device.m.get_gripper_joint_speed(int(joint))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
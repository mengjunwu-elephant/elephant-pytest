import pytest
import allure
from time import sleep

from common1 import logger
from common1.assert_utils import assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_joint_angle")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    for i in range(6):
        dev.m.set_gripper_joint_angle(i + 1, 0)
        sleep(2)
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_gripper(device):
    """重置夹爪所有关节到零位"""
    yield
    for i in range(6):
        device.m.set_gripper_joint_angle(i + 1, 0)
        sleep(0.5)

@allure.feature("设置夹爪关节角度")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])
def test_set_gripper_joint_angle(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_joint:{case["joint"]}')
        logger.debug(f'test_angle:{case["angle"]}')

    with allure.step(f"调用 set_gripper_joint_angle 接口,joint={case['joint']}, angle={case['angle']}"):
        if case['joint'] == 1:
            device.m.set_gripper_joint_angle(4,90)
        set_res = device.m.set_gripper_joint_angle(case["joint"], case["angle"])
        sleep(2)
        get_res = device.m.get_gripper_joint_angle(case["joint"])
        logger.debug(f"set_res:{set_res},get_res:{get_res}")

    with allure.step(f"断言返回值类型为int"):
        assert isinstance(set_res, int),f"返回类型错误，期望int，实际{type(set_res)}"

    with allure.step("断言设置返回值"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(set_res , expected), f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言获取返回值"):
        allure.attach(str(case["angle"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, case["angle"],tol=3,name='设置夹爪角度')

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("设置夹爪关节角度")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_joint_angle_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_joint:{case["joint"]}')
        logger.debug(f'test_angle:{case["angle"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 joint={case['joint']}, angle={case['angle']}"):
        with pytest.raises(ValueError, match=".*"):
            device.m.set_gripper_joint_angle(case["joint"], case["angle"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

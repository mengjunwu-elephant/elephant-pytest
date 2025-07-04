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

@allure.feature("设置夹爪关节角度-正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])
def test_set_gripper_joint_angle(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_joint:{case["joint"]}')
    logger.debug(f'test_angle:{case["angle"]}')

    set_res = device.m.set_gripper_joint_angle(case["joint"], case["angle"])
    sleep(2)
    get_res = device.m.get_gripper_joint_angle(case["joint"])

    if type(set_res) == int:
        logger.debug('请求类型断言成功')
    else:
        logger.debug(f'请求类型断言失败，实际类型为{type(set_res)}')

    try:
        assert_almost_equal(set_res, case['expect_data'])
        assert_almost_equal(get_res, case["angle"])
    except AssertionError as e:
        logger.exception('请求结果断言失败')
        logger.debug(f'期望数据：{case["angle"]}')
        logger.debug(f'实际结果：{get_res}')
        pytest.fail(f"用例【{case['title']}】断言失败: {e}")

    logger.info(f'请求结果断言成功，用例【{case["title"]}】测试成功')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置夹爪关节角度-异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_joint_angle_exception(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_joint:{case["joint"]}')
    logger.debug(f'test_angle:{case["angle"]}')

    with pytest.raises(ValueError, match=f".*{case['title']}.*"):
        device.m.set_gripper_joint_angle(case["joint"], case["angle"])

    logger.info(f'请求结果断言成功，用例【{case["title"]}】测试成功')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

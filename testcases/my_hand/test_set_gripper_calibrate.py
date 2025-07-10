import pytest
import allure
from time import sleep

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_joint_calibration")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    dev.m.set_gripper_joint_angle(4, 100)  # 放大1关节零位运动范围
    sleep(1)
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪关节校准")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])
def test_set_gripper_joint_calibration(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_joints:{case["joint"]}')

    set_res = device.m.set_gripper_joint_calibration(case["joint"])
    sleep(3)

    assert isinstance(set_res, int), f"返回类型断言失败，实际类型为{type(set_res)}"
    assert set_res == case['expect_data'], f"设置返回断言失败，期望：{case['expect_data']}，实际：{set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("设置夹爪关节校准")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_joint_calibration_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_joints:{case["joint"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 joint={case['joint']}"):
        with pytest.raises(ValueError, match=f".*{case['title']}.*"):
            device.m.set_gripper_joint_calibration(int(case['joint']))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

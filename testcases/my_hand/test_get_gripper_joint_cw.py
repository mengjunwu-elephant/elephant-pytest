import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "get_gripper_joint_cw")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]

@allure.feature("获取夹爪关节CW")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_get_gripper_joint_cw(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_joint:{case["joint"]}')

    with allure.step("调用 get_gripper_joint_cw 接口"):
        response = device.m.get_gripper_joint_cw(case["joint"])
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言返回值等于期望值"):
        allure.attach(str(case['expect_data']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"返回值不匹配，期望 {case['expect_data']}，实际 {response}"

    logger.info(f'✅ 用例【{case["title"]}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("获取夹爪关节CW")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_get_gripper_joint_cw_out_limit(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api:{case["api"]}')
        logger.debug(f'test_joint:{case["joint"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 joint={case['joint']}"):
        with pytest.raises(ValueError, match=".*"):
            device.m.get_gripper_joint_cw(int(case["joint"]))

    logger.info(f'✅ 用例【{case["title"]}】测试通过（异常断言）')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

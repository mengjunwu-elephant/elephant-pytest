import pytest
import allure
from common1 import logger
from common1.assert_utils import assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从 Excel 中提取测试数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "get_gripper_angles")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取夹爪角度")
@allure.story("获取夹爪当前角度")
@pytest.mark.parametrize("case", cases, ids=[case["title"] for case in cases])
def test_get_gripper_angles(device, case):
    expected = eval(case["expect_data"])
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 get_gripper_angles 接口"):
        response = device.m.get_gripper_angles()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误，应为 list，实际为 {type(response)}"


    with allure.step("断言返回值等于期望值"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,expected,tol=3,name='读取夹爪全角度')

    logger.info(f'✅ 用例【{case["title"]}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
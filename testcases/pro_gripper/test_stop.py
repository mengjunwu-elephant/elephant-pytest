import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 从Excel中提取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "stop")


@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("夹爪停止接口")
@allure.story("功能测试")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_stop(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')
        allure.attach(str(case["parameter"]), name="请求参数", attachment_type=allure.attachment_type.TEXT)

    with allure.step("设置夹爪绝对值为100，准备停止动作"):
        device.m.set_abs_gripper_value(100)

    with allure.step("调用停止接口"):
        response = device.m.set_gripper_stop()
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), name="接口返回值", attachment_type=allure.attachment_type.TEXT)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言返回结果与期望一致"):
        allure.attach(str(case["expect_data"]), name="期望返回值", attachment_type=allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"期望返回：{case['expect_data']}，实际返回：{response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

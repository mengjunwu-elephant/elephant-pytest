import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 读取测试用例数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "get_gripper_cww")

@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取夹爪CWW值")
@allure.story("正常用例")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_gripper_cww(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case.get("parameter", "")}')

    with allure.step("调用 get_gripper_cww 接口"):
        response = device.m.get_gripper_cww()
        logger.debug(f"接口返回值: {response}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，期望 int，实际为 {type(response)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言返回值正确"):
        allure.attach(str(case["expect_data"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

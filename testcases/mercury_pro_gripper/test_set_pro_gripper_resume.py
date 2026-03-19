import pytest
import allure

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

# 从 Excel 中提取测试数据
cases = get_test_data_from_excel(MercuryBase.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper_resume")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置Pro夹爪恢复动作")
@allure.story("夹爪恢复 resume 功能验证")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_set_pro_gripper_resume(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case.get('parameter', '')}")

    with allure.step("调用 set_pro_gripper_resume 接口"):
        response = device.mc.set_pro_gripper_resume()
        allure.attach(str(response), "恢复接口返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言接口返回值等于期望值"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(response),'实际值',allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

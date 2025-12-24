import time

import pytest
import allure
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from common1 import logger
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE, "get_gripper_angle")

@pytest.fixture(scope="module")
def device():
    dev = UltraArmP1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取Pro夹爪角度")
@allure.story("正常用例")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_pro_gripper_angle(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("调用 set_gripper_angle接口设置夹爪角度"):
        device.mc.set_gripper_angle(case['parameter'],100)
        logger.debug(f"接口返回值: {case['parameter']}")
        time.sleep(5)
    with allure.step("调用接口获取夹爪角度"):
        response = device.mc.get_gripper_angle()
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "接口返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值与期望值一致"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert_almost_equal(response,case['expect_data'],2,'读取角度'), f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
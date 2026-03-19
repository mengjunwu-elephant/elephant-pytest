import pytest
import allure

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 获取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_coords")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("get_coords 接口测试")
@allure.story("获取双臂坐标")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_coords(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    allure.dynamic.title(case["title"])

    with allure.step("调试信息记录"):
        logger.debug("test_api: {}".format(case["api"]))
        logger.debug("test_parameter: {}".format(case["parameter"]))

    with allure.step("机械臂请求发送"):
        response = device.mc.get_coords(eval(case['parameter']))
        logger.debug(f"机械臂返回值: {response}")
    with allure.step("类型断言"):
        assert isinstance(response, list), f"机械臂返回类型错误，实际为: {type(response)}"

    with allure.step('断言 get_angles 接口返回值是否匹配预期'):
        allure.attach(str(case['l_expect_data']), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,eval(case['l_expect_data']),tol=3,name='机械臂获取全坐标'), f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

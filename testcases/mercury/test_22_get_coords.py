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
    dev.go_zero()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("get_coords 接口测试")
@allure.story("获取机械臂全坐标")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
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

    with allure.step("list 长度断言"):
        assert len(response) == case['list_len'], f"机械臂返回列表长度不一致，期望: {case['list_len']}，实际: {response}"

    with allure.step('断言 get_angles 接口返回值是否匹配预期'):
        allure.attach(str(case['l_expect_data']), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(response,eval(case['l_expect_data']),tol=3,name='机械臂获取全坐标'), f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("get_coords 接口测试")
@allure.story("仅上电获取机械臂全坐标")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("机械臂获取机械臂全坐标"):
        response = device.mc.get_coords()
    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("get_coords 接口测试")
@allure.story("下电获取机械臂全坐标")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("机械臂获取机械臂全坐标"):
        response = device.mc.get_coords()
    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
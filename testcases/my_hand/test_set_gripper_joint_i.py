import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_joint_i")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_i()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("夹爪关节I值设置")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_joint_i(device, case):
    title = case['title']
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_joint: {case["joint"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step(f"调用接口 set_gripper_joint_I，joint={case['joint']}，parameter={case['parameter']}"):
        set_res = device.m.set_gripper_joint_I(case["joint"], case["parameter"])
        get_res = device.m.get_gripper_joint_I(case["joint"])
        logger.debug(f"接口返回 set: {set_res}, get: {get_res}")

    with allure.step("断言返回类型为int"):
        assert isinstance(set_res, int), f"返回类型错误，期望int，实际{type(set_res)}"

    with allure.step("断言返回值符合预期"):
        allure.attach(str(case['expect_data']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口返回值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == case['expect_data'], f"用例【{title}】断言失败，期望 {case['expect_data']}，实际 {set_res}"
        assert get_res == case["parameter"], f"用例【{title}】查询断言失败，期望 {case['parameter']}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试成功')

@allure.feature("夹爪关节I值设置")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_joint_i_exception(device, case):
    title = case['title']
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step(f"调用接口 set_gripper_joint_I，joint={case['joint']}，parameter={case['parameter']}，预期触发异常"):
        with pytest.raises(ValueError, match=f".*I值为{case['parameter']}.*"):
            device.m.set_gripper_joint_I(case["joint"], case["parameter"])

    logger.info(f'✅ 用例【{title}】异常断言通过')

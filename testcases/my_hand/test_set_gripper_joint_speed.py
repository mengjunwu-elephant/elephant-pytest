import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 读取测试数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_joint_speed")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_speed()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("夹爪关节速度设置")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_joint_speed(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_joint: {case["joint"]}')
        logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step(f"调用 {case['api']}，joint={case['joint']}，parameter={case['parameter']}"):
        set_res = device.m.set_gripper_joint_speed(case["joint"], case["parameter"])
        get_res = device.m.get_gripper_joint_speed(case["joint"])
        logger.debug(f"接口返回 set: {set_res}, get: {get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，应为 int，实际为 {type(set_res)}"

    with allure.step("断言设置结果和查询结果"):
        allure.attach(str(case['expect_data']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口返回值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == case['expect_data'], f"用例【{title}】set接口断言失败，期望 {case['expect_data']}，实际 {set_res}"
        assert get_res == case["parameter"], f"用例【{title}】get接口断言失败，期望 {case['parameter']}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("夹爪关节速度设置")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_joint_speed_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_joint: {case["joint"]}')
        logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，joint={case['joint']}，parameter={case['parameter']}"):
        with pytest.raises(ValueError, match=f".*速度值为{case['parameter']}.*"):
            device.m.set_gripper_joint_speed(case["joint"], case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

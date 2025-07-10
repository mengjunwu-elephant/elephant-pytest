import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_gripper_min_pressure")


@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_mini_pressure(0)
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪最小启动力")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_min_pressure_normal(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("发送设置最小启动力指令"):
        set_res = device.m.set_gripper_mini_pressure(case["parameter"])
        logger.debug(f"设置返回值: {set_res}")

    with allure.step("读取当前最小启动力值"):
        get_res = device.m.get_gripper_mini_pressure()
        logger.debug(f"读取返回值: {get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(get_res, int), f"返回类型错误，期望 int，实际为 {type(get_res)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言读取返回值与预期一致"):
        allure.attach(str(case["expect_data"]), name="设置接口期望返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(case['value']), name="读取接口期望返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(set_res, name='设置接口实际返回值', attachment_type=allure.attachment_type.TEXT)
        allure.attach(get_res, name='读取接口实际返回值', attachment_type=allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望返回：{case['expect_data']}，实际返回：{set_res}"
        assert get_res == case['parameter'], f"期望返回：{case['parameter']}，实际返回：{get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪最小启动力")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_min_pressure_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("断言非法值触发 ValueError"):
        with pytest.raises(ValueError, match="value错误"):
            device.m.set_gripper_mini_pressure(case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

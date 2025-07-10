import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_gripper_enabled")


@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪使能")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_enabled_normal(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("调用 set_gripper_enable 设置使能状态"):
        response = device.m.set_gripper_enable(case["parameter"])
        logger.debug(f"接口返回结果：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，期望 int，实际为 {type(response)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言返回结果与期望值一致"):
        allure.attach(str(case["expect_data"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"期望返回：{case['expect_data']}，实际返回：{response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪使能")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_enabled_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("断言非法参数抛出 ValueError"):
        with pytest.raises(ValueError):
            device.m.set_gripper_enable(case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

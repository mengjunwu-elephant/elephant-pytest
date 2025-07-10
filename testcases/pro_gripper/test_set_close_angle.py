import pytest
import allure
from settings import ProGripperBase
from common1.test_data_handler import get_test_data_from_excel
from common1 import logger

# 从Excel读取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_close_angle")

@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_io_close_value(0)  # 恢复默认闭合角度
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置闭合角度")
@allure.story("正常设置闭合角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_close_angle(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step(f"调用 set_gripper_io_close_value({case['parameter']})"):
        response = device.m.set_gripper_io_close_value(case["parameter"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，期望 int，实际为 {type(response)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言返回结果符合预期"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"期望值：{case['expect_data']}，实际值：{response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置闭合角度")
@allure.story("异常值测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_close_angle_out_of_limit(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step(f"调用 set_gripper_io_close_value({case['parameter']}) 并期望抛出 ValueError"):
        with pytest.raises(ValueError, match=".*"):
            device.m.set_gripper_io_close_value(case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


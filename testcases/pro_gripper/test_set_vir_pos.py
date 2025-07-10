import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 从Excel获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_vir_pos")


@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_vir_pos(8)  # 恢复默认虚位
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪虚位")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_vir_pos_normal(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')
        allure.attach(str(case["parameter"]), name="请求参数", attachment_type=allure.attachment_type.TEXT)

    with allure.step("设置夹爪虚位"):
        set_res = device.m.set_gripper_vir_pos(case["parameter"])
        logger.debug(f"设置返回值: {set_res}")

    with allure.step("读取当前夹爪虚位"):
        get_res = device.m.get_gripper_vir_pos()
        logger.debug(f"读取返回值: {get_res}")

    with allure.step("断言返回值类型"):
        assert isinstance(set_res, int), f"返回类型错误，应为 int，实际为 {type(set_res)}"

    with allure.step("断言设置结果与期望一致"):
        allure.attach(str(case["expect_data"]), name="期望设置返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际设置返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际读取虚位", attachment_type=allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望设置返回值：{case['expect_data']}，实际：{set_res}"
        assert get_res == case["parameter"], f"读取虚位不一致，期望：{case['parameter']}，实际：{get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪虚位")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_vir_pos_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印异常测试参数"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("断言非法参数触发 ValueError"):
        with pytest.raises(ValueError):
            device.m.set_gripper_vir_pos(case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

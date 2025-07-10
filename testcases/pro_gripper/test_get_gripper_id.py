import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_gripper_id")

@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束恢复默认ID，关闭连接
    dev.m.set_gripper_Id(14)
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪ID")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_id(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("调用接口 set_gripper_Id 设置ID"):
        set_res = device.m.set_gripper_Id(case["parameter"])
        logger.debug(f"设置返回结果：{set_res}")

    with allure.step("调用接口 get_gripper_Id 获取当前ID"):
        get_res = device.m.get_gripper_Id()
        logger.debug(f"获取到的ID：{get_res}")

    with allure.step("断言设置接口返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言设置接口返回值是否符合预期"):
        assert set_res == case["expect_data"], f"期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取的ID与设置值一致"):
        assert get_res == case["parameter"], f"期望ID：{case['parameter']}，实际ID：{get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪ID")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_id_out_limit(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("断言设置ID超限触发异常 ValueError"):
        with pytest.raises(ValueError, match=f".*{case['parameter']}.*"):
            device.m.set_gripper_Id(int(case["parameter"]))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 获取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_gripper_cw")


@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_cw(3)  # 恢复默认值
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置夹爪CW参数")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_gripper_cw_normal(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("调用 set_gripper_cw 设置CW值"):
        set_res = device.m.set_gripper_cw(case["parameter"])
        logger.debug(f"设置返回值：{set_res}")

    with allure.step("调用 get_gripper_cw 获取CW值进行验证"):
        get_res = device.m.get_gripper_cw()
        logger.debug(f"获取返回值：{get_res}")

    with allure.step("断言返回类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言设置与返回值是否正确"):
        allure.attach(str(case["expect_data"]), name="期望设置返回", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际设置返回", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际CW值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望设置返回：{case['expect_data']}，实际：{set_res}"
        assert get_res == case["parameter"], f"设置值与读取值不一致：期望 {case['parameter']}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪CW参数")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_gripper_cw_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("断言设置CW值超范围应抛出 ValueError"):
        with pytest.raises(ValueError):
            device.m.set_gripper_cw(case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

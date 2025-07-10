import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import ProGripperBase

# 读取测试数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_protection_current")

@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_protection_current(300)  # 恢复默认保护电流
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置保护电流")
@allure.story("正常值测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_protection_current_normal(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    with allure.step("打印参数"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}")

    with allure.step("发送设置保护电流请求"):
        set_res = device.m.set_gripper_protection_current(case["parameter"])
        logger.debug(f"设置返回值: {set_res}")

    with allure.step("读取保护电流当前值"):
        get_res = device.m.get_gripper_protection_current()
        logger.debug(f"读取返回值: {get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，期望 int，实际为 {type(set_res)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言返回值与预期一致"):
        allure.attach(str(case["expect_data"]), name="期望返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际返回值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == case["expect_data"], f"期望返回：{case['expect_data']}，实际返回：{get_res}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")


@allure.feature("设置保护电流")
@allure.story("异常值测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_protection_current_exception(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    with allure.step("打印异常参数"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}")

    with allure.step("尝试设置异常值并捕获 ValueError"):
        with pytest.raises(ValueError, match="value错误"):
            device.m.set_gripper_protection_current(case["parameter"])

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

import pytest
import allure
from pymycobot.error import MercuryDataException, MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从 Excel 提取用例
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "resume")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("resume 接口测试")
@allure.story("正常 resume 场景")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_resume_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: {case['parameter']}")

    with allure.step("先调用 pause"):
        device.mc.pause()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.resume(case["parameter"])

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("resume 接口测试")
@allure.story("异常 resume 场景")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_resume_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: {case['parameter']}")

    with allure.step("调用 resume 接口并断言抛出 MyCobotPro450DataException"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.resume(case["parameter"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
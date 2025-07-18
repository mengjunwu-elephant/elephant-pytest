import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "is_power_on")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取机械臂上电状态")
@allure.story("机械臂下电情况上电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_expected:{expected}')

    with allure.step("调用 power_off 接口"):
        device.mc.power_off()

    with allure.step('调用is_power_on 接口'):
        res = device.mc.is_power_on()
        logger.debug(f"接口返回：{res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(res,int), f"返回类型错误，应为 int，实际为 {type(res)}"

    with allure.step("断言接口返回结果，is_power_on状态"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("获取机械臂上电状态")
@allure.story("机械臂上电情况上电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_power_on(device, case):
    title = case["title"]
    expected = case["expect_data"]


    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_expected:{expected}')

    with allure.step("调用 power_on 接口"):
        device.mc.power_on()

    with allure.step('调用is_power_on 接口'):
        res = device.mc.is_power_on()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(res, int), f"返回类型错误，应为 int，实际为 {type(res)}"

    with allure.step("断言接口返回结果，is_power_on状态"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {res}"


    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "clear_error_information")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("清除机械臂运动报错信息")
@allure.story("正确清除机械臂报错信息")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_clear_error_information(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('使机械臂运动到坐标初始位置'):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step('使机械臂运动到超限坐标'):
        device.mc.send_coord(1,300, device.speed)
        device.wait()

    with allure.step('调用 get_error_information 接口'):
        get_res = device.mc.get_error_information()
        logger.debug(f"接口返回：{get_res}")

    with allure.step("调用 clear_error_information 接口"):
        set_res = device.mc.clear_error_information()
        logger.debug(f"接口返回：{set_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误，应为 int，实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step('清除报错信息'):
        device.mc.clear_error_information()

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

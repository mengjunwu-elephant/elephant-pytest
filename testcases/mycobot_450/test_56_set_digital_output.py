import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "set_digital_output")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    input('请确认末端IO测试工具已连接,点击回车继续测试')
    yield dev
    dev.default_digital_io_output()
    #dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置末端IO输出")
@allure.story("正确设置末端IO输出")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_digital_output1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'pin_no:{case["pin_no"]}')
    logger.debug(f'state:{case["state"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        time.sleep(1)
        set_res = device.mc.set_digital_output(case["pin_no"],case["state"])
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f"调用 get_digital_input 接口"):
        get_res = device.mc.get_digital_input(case["pin_no"])
        logger.debug(f"接口返回：{get_res}")

    with allure.step('判断末端IO是否设置成功'):
        result = input(f'当前设置引脚为{case["pin_no"]}请观察末端IO设置时是否有响声，输入0测试失败')
        if result == '0':
            assert False, f"用例【{title}】测试失败，期望末端IO设置成功，实际末端IO设置失败"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言末端IO读取值查看是否设置成功"):
        allure.attach(str(case['state']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == case['state'], f"用例【{title}】断言失败，期望 {case['state']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置末端IO输出")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_digital_output_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'pin_no:{case["pin_no"]}')
    logger.debug(f'state:{case["state"]}')

    with allure.step(f"断言抛出 Mycobot450Exception,引脚为{case['pin_no']}，状态为{case['state']}"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.set_digital_output(case['pin_no'],case['state'])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

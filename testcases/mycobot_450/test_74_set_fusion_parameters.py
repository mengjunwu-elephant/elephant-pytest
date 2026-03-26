import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "set_fusion_parameters")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_fusion_parameters()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置速度融合规划参数")
@allure.story("正确设置速度融合规划参数")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_fusion_parameters1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'rank:{case["rank"]}')
    logger.debug(f'value:{case["value"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        if case['rank'] != 0:
            set_res = device.mc.set_fusion_parameters(case['rank'],case["value"])
            time.sleep(1)
            logger.debug(f"接口返回：{set_res}")
        else:
            set_res = device.mc.set_fusion_parameters(case['rank'])
            logger.debug(f"接口返回：{set_res}")

    with allure.step('调用 get_fusion_parameters 接口'):
        if case['rank'] != 0:
            get_res = device.mc.get_fusion_parameters(case['rank'])
            logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言是否设置成功"):
        if case['rank'] != 0:
            allure.attach(str(case['value']), name="期望值", attachment_type=allure.attachment_type.TEXT)
            allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
            assert get_res == case['value'], f"用例【{title}】断言失败，期望 {case['value']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置速度融合规划参数")
@allure.story("正确设置速度融合规划参数")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_tool_serial_timeout_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'rank:{case["rank"]}')
    logger.debug(f'value:{case["value"]}')

    with allure.step(f"断言抛出 Mycobot450Exception,参数为{case['rank']}，值为{case['value']}"):
        with pytest.raises(MyCobotPro450DataException) as exc:
            device.mc.set_fusion_parameters(case['rank'],case["value"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
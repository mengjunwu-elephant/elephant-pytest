import time

import pytest
import allure
from pymycobot.error import MyCobot280DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot280Base

# 从 Excel 提取用例
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "set_hts_gripper_torque")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.set_HTS_gripper_torque(dev.hts_gripper_torque)
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("set_hts_gripper_torque 接口测试")
@allure.story("正常 set_hts_gripper_torque 场景")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_hts_gripper_torque_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: {case['parameter']}")

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_HTS_gripper_torque(case['parameter'])

    with allure.step('调用 get_hts_gripper_torque 接口'):
        get_res = device.mc.get_HTS_gripper_torque()
    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step('断言 get_hts_gripper_torque 返回结果'):
        allure.attach(str(case['parameter']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == case['parameter'], f"用例【{title}】断言失败，期望 {case['parameter']},实际 {get_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("set_hts_gripper_torque 接口测试")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_set_hts_gripper_torque_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}")

    with allure.step("断言抛出 MyCobot280DataException"):
        with pytest.raises(MyCobot280DataException) as exc:
            device.mc.set_HTS_gripper_torque(param)

    logger.info(f"✅ 用例【{title}】异常测试通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
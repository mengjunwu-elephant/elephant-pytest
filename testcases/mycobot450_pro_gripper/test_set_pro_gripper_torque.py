import time

import pytest
import allure
from pymycobot.error import MercuryDataException, MyCobotPro450DataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import Mycobot450Base

# 提取测试数据
cases = get_test_data_from_excel(Mycobot450Base.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper_torque")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_pro_gripper_torque(100)
    time.sleep(3)
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置Pro夹爪扭矩 - 正常值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_pro_gripper_torque_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step("调用 set_pro_gripper_torque 设置值"):
        set_res = device.mc.set_pro_gripper_torque(case["parameter"])
        allure.attach(str(set_res), "设置返回值", allure.attachment_type.TEXT)

    with allure.step("调用 get_pro_gripper_torque 获取当前值"):
        get_res = device.mc.get_pro_gripper_torque()
        allure.attach(str(get_res), "当前扭矩值", allure.attachment_type.TEXT)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"类型错误，返回类型为 {type(set_res)}"

    with allure.step("断言设置返回值与期望相符"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望 {case['expect_data']}，实际 {set_res}"

    with allure.step("断言获取值与设置值一致"):
        allure.attach(str(case['parameter']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(get_res),'实际值',allure.attachment_type.TEXT)
        assert get_res == case["parameter"], f"期望值为 {case['parameter']}，实际值为 {get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")


@allure.feature("设置Pro夹爪扭矩")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_pro_gripper_torque_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameter']}")

    with allure.step(f"断言设置异常值时抛出 MyCobotPro450DataException，扭矩为{case['parameter']}"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.set_pro_gripper_torque(case["parameter"])

    logger.info(f"✅ 异常用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

import time

import pytest
import allure
from pymycobot.error import MercuryDataException, MyCobotPro450DataException

from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from common1 import logger
from settings import MercuryE1Base

# 加载测试数据
cases = get_test_data_from_excel(MercuryE1Base.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper_angle")


@pytest.fixture(scope="module")
def device():
    dev = MercuryE1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_pro_gripper_angle(0)
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置Pro夹爪角度")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_pro_gripper_angle_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step("调用设置接口"):
        set_res = device.mc.set_pro_gripper_angle(case["value"])
        time.sleep(5)
        allure.attach(str(set_res), "设置接口返回值", allure.attachment_type.TEXT)
        logger.debug(f'接口返回：{set_res}')

    with allure.step("调用获取接口"):
        get_res = device.mc.get_pro_gripper_angle()
        allure.attach(str(get_res), "获取接口返回值", allure.attachment_type.TEXT)
        logger.debug(f'接口返回：{get_res}')

    with allure.step("断言设置接口返回值类型为 int"):
        assert isinstance(set_res, int), f"类型错误，实际为 {type(set_res)}"

    with allure.step("断言设置返回值正确"):
        allure.attach(str(case['expect_data']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(set_res),'实际值',allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言获取值与设置值一致"):
        allure.attach(str(case['value']),'期望值',allure.attachment_type.TEXT)
        allure.attach(str(get_res),'实际值',allure.attachment_type.TEXT)
        assert_almost_equal(get_res,case["value"],tol=2,name='设置角度'), f"期望：{case['value']}，实际：{get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置Pro夹爪角度")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_pro_gripper_angle_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step(f"断言设置接口抛出 MyCobotPro450DataException, value: {case['value']}"):
        with pytest.raises(MyCobotPro450DataException) as exc:
            device.mc.set_pro_gripper_angle(case["value"])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功,异常信息：{exc.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
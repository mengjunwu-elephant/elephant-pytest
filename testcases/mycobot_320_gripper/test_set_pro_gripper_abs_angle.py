import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import Mycobot320Base

cases = get_test_data_from_excel(Mycobot320Base.GRIPPER_TEST_DATA_FILE, "set_pro_gripper_abs_angle")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    sleep(3)
    dev.m.m.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_gripper(device):
    yield
    device.m.set_pro_gripper_abs_angle(0)
    sleep(3)

if
@allure.feature("设置Pro夹爪绝对角度")
@allure.story("设置角度 - 正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 1], ids=lambda c: c["title"])
def test_set_pro_gripper_abs_angle(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step("调用设置接口"):
        response = device.m.set_pro_gripper_abs_angle(case["value"])
        allure.attach(str(response), "设置返回值", allure.attachment_type.TEXT)
        sleep(3)

    with allure.step("断言类型为 int"):
        assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值正确"):
        assert response == case["expect_data"], f"期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")


@allure.feature("设置Pro夹爪绝对角度")
@allure.story("暂停与恢复 - 功能验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 2], ids=lambda c: c["title"])
def test_pause_and_resume(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    with allure.step("设置角度为100"):
        abs_res = device.m.set_pro_gripper_abs_angle(100)
        allure.attach(str(abs_res), "设置角度返回", allure.attachment_type.TEXT)
        sleep(0.5)

    with allure.step("调用暂停接口"):
        pause_res = device.m.set_pro_gripper_pause()
        allure.attach(str(pause_res), "暂停返回", allure.attachment_type.TEXT)
        sleep(3)

    with allure.step("调用恢复接口"):
        resume_res = device.m.set_pro_gripper_resume()
        allure.attach(str(resume_res), "恢复返回", allure.attachment_type.TEXT)
        sleep(1)

    with allure.step("断言所有返回值为 int"):
        assert all(isinstance(r, int) for r in [abs_res, pause_res, resume_res])

    with allure.step("断言返回值均正确"):
        assert abs_res == case["expect_data"]
        assert pause_res == case["expect_data"]
        assert resume_res == case["expect_data"]

    logger.info(f"✅ 用例【{case['title']}】测试成功")


@allure.feature("设置Pro夹爪绝对角度")
@allure.story("停止功能测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 3], ids=lambda c: c["title"])
def test_stop(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    with allure.step("调用设置绝对值接口"):
        abs_res = device.m.set_abs_gripper_value(100)
        allure.attach(str(abs_res), "设置绝对值返回", allure.attachment_type.TEXT)
        sleep(0.5)

    with allure.step("调用停止接口"):
        stop_res = device.m.set_pro_gripper_stop()
        allure.attach(str(stop_res), "停止返回", allure.attachment_type.TEXT)

    with allure.step("断言所有返回值为 int"):
        assert isinstance(abs_res, int)
        assert isinstance(stop_res, int)

    with allure.step("断言返回值均正确"):
        assert abs_res == case["expect_data"]
        assert stop_res == case["expect_data"]

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置Pro夹爪绝对角度")
@allure.story("越界异常测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_out_limit(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step(f"断言触发 MercuryDataException, value: {case['value']}"):
        with pytest.raises(MercuryDataException):
            device.m.set_pro_gripper_abs_angle(case["value"])

    logger.info(f"✅ 用例【{case['title']}】异常断言成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
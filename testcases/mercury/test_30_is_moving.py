import pytest
import allure
from time import sleep

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "is_moving")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_device(device):
    # 每个测试前初始化极限开关和坐标
    device.ml.set_limit_switch(2, 0)
    device.mr.set_limit_switch(2, 0)
    device.init_coords()
    yield
    device.go_zero()
    sleep(2)


@allure.feature("is_moving 接口测试")
@allure.story("正常状态检测")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_is_moving_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step("获取左右臂运动状态"):
        l_response = device.ml.is_moving()
        r_response = device.mr.is_moving()

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂类型错误: {type(l_response)}"
        assert isinstance(r_response, int), f"右臂类型错误: {type(r_response)}"

    with allure.step("断言返回结果与期望一致"):
        assert l_response == case["l_expect_data"], f"左臂期望 {case['l_expect_data']}，实际 {l_response}"
        assert r_response == case["r_expect_data"], f"右臂期望 {case['r_expect_data']}，实际 {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")


@allure.feature("is_moving 接口测试")
@allure.story("调用 stop 后状态检测")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal1"], ids=lambda c: c["title"])
def test_is_moving_after_stop(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step("先调用 stop 停止运动"):
        device.ml.stop()
        device.mr.stop()
        sleep(2)

    with allure.step("检测左右臂是否仍在运动"):
        l_response = device.ml.is_moving()
        r_response = device.mr.is_moving()

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂类型错误: {type(l_response)}"
        assert isinstance(r_response, int), f"右臂类型错误: {type(r_response)}"

    with allure.step("断言返回结果与期望一致"):
        assert l_response == case["l_expect_data"], f"左臂期望 {case['l_expect_data']}，实际 {l_response}"
        assert r_response == case["r_expect_data"], f"右臂期望 {case['r_expect_data']}，实际 {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")

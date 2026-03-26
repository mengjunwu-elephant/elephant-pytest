import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "is_in_position")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("is_in_position 接口测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] in ["normal","left","right"]], ids=lambda c: c["title"])
def test_is_in_position_normal(device, case):
    title = case["title"]
    param = eval(case["parameter"])
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step('使机械臂运动到初始点位'):
        device.ml.send_angles(device.coords_init_angles,device.speed)
        device.mr.send_angles(device.coords_init_angles,device.speed)
        device.wait()
        if mode == 1:
            logger.info(f'当前左臂坐标为{device.ml.get_coords()}')
            logger.info(f'当前右臂坐标为{device.mr.get_coords()}')
        elif mode == 2:
            logger.info(f'当前左臂坐标为{device.ml.get_base_coords()}')
            logger.info(f'当前右臂坐标为{device.mr.get_base_coords()}')

    with allure.step("调用 is_in_position 接口进行 is_in_position 测试"):
        if case["test_type"] == "normal":
            l_response = device.ml.is_in_position(param, mode)
            r_response = device.mr.is_in_position(param, mode)
        elif case["test_type"] == "left":
            l_response = device.ml.is_in_position(param, mode)
        elif case["test_type"] == "right":
            r_response = device.mr.is_in_position(param, mode)

    with allure.step("断言返回类型为 int"):
        if case["test_type"] == "normal":
            assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型错误: {type(r_response)}"
        elif case["test_type"] == "left":
            assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"
        elif case["test_type"] == "right":
            assert isinstance(r_response, int), f"右臂返回类型错误: {type(r_response)}"

    with allure.step("断言返回值是否符合预期"):
        if case["test_type"] == "normal":
            assert l_response == case["l_expect_data"], f"左臂期望值 {case['l_expect_data']}，实际为 {l_response}"
            assert r_response == case["r_expect_data"], f"右臂期望值 {case['r_expect_data']}，实际为 {r_response}"
        elif case["test_type"] == "left":
            assert l_response == case["l_expect_data"], f"左臂期望值 {case['l_expect_data']}，实际为 {l_response}"
        elif case["test_type"] == "right":
            assert r_response == case["r_expect_data"], f"右臂期望值 {case['r_expect_data']}，实际为 {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("is_in_position 接口测试")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_is_in_position_exception(device, case):
    title = case["title"]
    param = case["parameter"]
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step("断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc:
            device.ml.is_in_position(param, mode)
            device.mr.is_in_position(param, mode)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

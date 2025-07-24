import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_base_rpy")


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


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
@allure.feature("Jog 基础旋转角度 RPY")
@allure.story("正常用例")
def test_jog_base_rpy(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        device.init_coords()

        logger.debug(f"API: {case['api']}, 轴: {case['axis']}, 参数: {case['parameter']}, 速度: {case['speed']}")

        with allure.step("调用左臂 jog_base_rpy"):
            l_response = device.ml.jog_base_rpy(case["axis"], case["parameter"], case["speed"])
            logger.debug(f"左臂响应: {l_response}")

        with allure.step("调用右臂 jog_base_rpy"):
            r_response = device.mr.jog_base_rpy(case["axis"], case["parameter"], case["speed"])
            logger.debug(f"右臂响应: {r_response}")

        with allure.step("断言左臂返回类型为 int"):
            assert isinstance(l_response, int), f"左臂返回类型错误，实际类型: {type(l_response)}"

        with allure.step("断言右臂返回类型为 int"):
            assert isinstance(r_response, int), f"右臂返回类型错误，实际类型: {type(r_response)}"

        with allure.step("断言左臂返回值"):
            assert l_response == case['l_expect_data'], f"左臂期望={case['l_expect_data']}，实际={l_response}"

        with allure.step("断言右臂返回值"):
            assert r_response == case['r_expect_data'], f"右臂期望={case['r_expect_data']}，实际={r_response}"

        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
@allure.feature("Jog 基础旋转角度 RPY")
@allure.story("异常用例")
def test_jog_base_rpy_exception(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        device.init_coords()
        logger.debug(f"API: {case['api']}, 轴: {case['axis']}, 参数: {case['parameter']}, 速度: {case['speed']}")

        with allure.step("调用左臂 jog_base_rpy，期望抛出 MercuryDataException"):
            with pytest.raises(MercuryDataException, match=f".*方向.*{case['parameter']}.*{case['speed']}.*"):
                device.ml.jog_base_rpy(case["axis"], case["parameter"], case["speed"])

        logger.info(f"✅ 用例【{title}】异常断言成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")

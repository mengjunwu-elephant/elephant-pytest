import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "write_move_c")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_coords(device):
    # 每个用例后自动重置坐标
    yield
    device.init_coords()


@allure.feature("轨迹接口")
@allure.story("正常写入轨迹点")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_write_move_c(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        transpoint = eval(case["transpoint"])
        endpoint = eval(case["endpoint"])
        speed = case["speed"]

        with allure.step("调用右臂 write_move_c 接口"):
            r_response = device.mr.write_move_c(transpoint, endpoint, speed)
            logger.debug(f"右臂响应: {r_response}")

        with allure.step("调用左臂 write_move_c 接口"):
            l_response = device.ml.write_move_c(transpoint, endpoint, speed)
            logger.debug(f"左臂响应: {l_response}")

        with allure.step("断言返回值类型"):
            assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

        with allure.step("断言返回结果是否符合预期"):
            expected_l = case["l_expect_data"]
            assert l_response == expected_l, f"左臂期望: {expected_l}, 实际: {l_response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("轨迹接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_write_move_c_exception(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        transpoint = eval(case["transpoint"])
        endpoint = eval(case["endpoint"])
        speed = case["speed"]

        with allure.step("断言左臂调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException):
                device.ml.write_move_c(transpoint, endpoint, speed)

        with allure.step("断言右臂调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException):
                device.mr.write_move_c(transpoint, endpoint, speed)

        logger.info(f"✅ 用例【{title}】异常断言成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

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
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_coords(device):
    # 每个用例前自动重置坐标
    device.init_coords()
    device.wait()
    yield


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

        with allure.step("调用机械臂 write_move_c 接口"):

            device.wait()

        with allure.step("调用机械臂 write_move_c 接口"):
            response = device.mc.write_move_c(transpoint, endpoint, speed)
            device.wait()
            logger.debug(f"机械臂响应: {response}")

        with allure.step("断言返回值类型"):
            assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"

        with allure.step("断言返回结果是否符合预期"):
            expected = case["l_expect_data"]
            assert response == expected, f"机械臂期望: {expected}, 实际: {response}"

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

        with allure.step("断言机械臂调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException):
                device.mc.write_move_c(transpoint, endpoint, speed)

        with allure.step("断言机械臂调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException) as exc_info:
                device.mc.write_move_c(transpoint, endpoint, speed)

        logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("轨迹接口")
@allure.story("仅上电调用 write_move_c 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        transpoint = eval(case["transpoint"])
        endpoint = eval(case["endpoint"])
        speed = case["speed"]

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("调用机械臂 write_move_c 接口"):
        response = device.mc.write_move_c(transpoint, endpoint, speed)
        device.wait()
        logger.debug(f"机械臂响应: {response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("轨迹接口")
@allure.story("下电调用 write_move_c 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        transpoint = eval(case["transpoint"])
        endpoint = eval(case["endpoint"])
        speed = case["speed"]

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("调用机械臂 write_move_c 接口"):
        response = device.mc.write_move_c(transpoint, endpoint, speed)
        device.wait()
        logger.debug(f"机械臂响应: {response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

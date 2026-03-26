import pytest
import allure
from pymycobot.error import MercuryE1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryE1Base

cases = get_test_data_from_excel(MercuryE1Base.TEST_DATA_FILE, "write_move_c")


@pytest.fixture(scope="module")
def device():
    dev = MercuryE1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("圆弧运动")
@allure.story("正常进行圆弧运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_write_move_c(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        transpoint = eval(case["transpoint"])
        endpoint = eval(case["endpoint"])
        speed = case["speed"]

        with allure.step('使机械臂运动到坐标初始位置'):
            device.mc.send_angles(device.coords_init_angles,device.speed)
            device.wait()

        with allure.step("调用 write_move_c 接口"):
            response = device.mc.write_move_c(transpoint, endpoint, speed)
            device.wait()
            logger.debug(f"接口响应: {response}")

        with allure.step("断言返回值类型"):
            assert isinstance(response, int), f"返回类型应为 int，实际为 {type(response)}"

        with allure.step("断言返回结果是否符合预期"):
            expected = case["expect_data"]
            assert response == expected, f"期望: {expected}, 实际: {response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("圆弧运动")
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

        with allure.step("断言调用接口时抛出 MercuryE1DataException 异常"):
            with pytest.raises(MercuryE1DataException) as exc:
                device.mc.write_move_c(transpoint, endpoint, speed)

        logger.info(f"✅ 用例【{title}】异常断言成功,异常信息：{exc.value}")
        logger.info(f"》》》用例【{title}】测试完成《《《")
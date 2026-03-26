import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import Mycobot450Base

cases = get_test_data_from_excel(Mycobot450Base.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper_io_open_angle")

@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_pro_gripper_io_close_angle(100)  # 恢复默认张开角度
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪张开角度")
@allure.story("正常值测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_open_angle_normal(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    with allure.step("打印参数"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}")

    with allure.step("发送设置请求"):
        response = device.mc.set_pro_gripper_io_close_angle(case["parameter"])
        logger.debug(f"设置返回值：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，期望 int，实际为 {type(response)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言返回值与预期一致"):
        allure.attach(str(case["expect_data"]), name="期望返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际返回值", attachment_type=allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"期望返回：{case['expect_data']}，实际返回：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")


@allure.feature("设置夹爪张开角度")
@allure.story("异常值测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_open_angle_exception(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")

    with allure.step("打印异常参数"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}")

    with allure.step("尝试设置异常值并捕获 MyCobotPro450DataException"):
        with pytest.raises(MyCobotPro450DataException) as exc:
            device.mc.set_pro_gripper_io_close_angle(case["parameter"])

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")
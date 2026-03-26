import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryE1Base

cases = get_test_data_from_excel(MercuryE1Base.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper_id")

@pytest.fixture(scope="module")
def device():
    dev = MercuryE1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.set_pro_gripper_id(14,10)  # 恢复默认 ID
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪 ID")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") != "exception"], ids=lambda c: c["title"])
def test_set_pro_gripper_id_normal(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("设置夹爪 ID"):
        set_res = device.mc.set_pro_gripper_id(case["parameter"])
        logger.debug(f"设置返回值: {set_res}")

    with allure.step("读取当前夹爪 ID"):
        get_res = device.mc.get_pro_gripper_id(10)
        logger.debug(f"读取返回值: {get_res}")

    with allure.step("断言返回值类型"):
        assert isinstance(set_res, int), f"返回类型错误，应为 int，实际为 {type(set_res)}"

    with allure.step("断言返回结果与期望一致"):
        allure.attach(str(case["expect_data"]), name="期望设置返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际设置返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际读取 ID", attachment_type=allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望设置返回值：{case['expect_data']}，实际：{set_res}"
        assert get_res == case["parameter"], f"读取 ID 不一致，期望：{case['parameter']}，实际：{get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("设置夹爪 ID")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_pro_gripper_id_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step("断言非法参数触发 MyCobotPro450DataException"):
        with pytest.raises(MyCobotPro450DataException) as exc:
            device.mc.set_pro_gripper_id(case["parameter"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')
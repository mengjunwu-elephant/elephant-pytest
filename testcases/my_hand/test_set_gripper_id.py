import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从 Excel 中提取数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_id")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.set_gripper_Id(14)  # 恢复默认 ID
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪ID")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])
def test_set_gripper_id(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step(f"调用 set_gripper_Id 接口设置ID为 {case['parameter']}"):
        set_res = device.m.set_gripper_Id(case["parameter"])

    with allure.step("调用 get_gripper_Id 接口获取当前ID"):
        get_res = device.m.get_gripper_Id()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"请求类型断言失败，实际类型为 {type(set_res)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言设置结果是否为期望值"):
        allure.attach(str(case["expect_data"]), name="期望返回值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际返回值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == case["expect_data"], f"期望：{case['expect_data']}，实际：{set_res}"

    with allure.step("断言读取ID是否为设置值"):
        allure.attach(str(case["parameter"]), name="期望ID", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际ID", attachment_type=allure.attachment_type.TEXT)
        assert get_res == case["parameter"], f"期望ID：{case['parameter']}，实际ID：{get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("设置夹爪ID")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_id_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口，参数 parameter={case['parameter']}"):
        with pytest.raises(ValueError, match=f".*{case['title']}.*"):
            device.m.set_gripper_Id(int(case["parameter"]))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

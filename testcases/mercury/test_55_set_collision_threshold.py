import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_collision_threshold")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 恢复默认阈值
    for i in range(7):
        dev.mc.set_collision_threshold(i + 1, 100)
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置碰撞阈值")
@allure.story("正常设置碰撞阈值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_collision_threshold_normal(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    response = device.mc.set_collision_threshold(joint, param)

    assert isinstance(response, int), f"机械臂响应类型错误: {type(response)}"

    assert response == case["l_expect_data"], f"机械臂响应错误: 期望={case['l_expect_data']}, 实际={response}"

    logger.info(f"✅ 用例【{title}】测试成功")

@allure.feature("设置碰撞阈值")
@allure.story("异常设置 - 越界/非法参数应抛异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_collision_threshold_exception(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    with allure.step("断言机械臂均抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_collision_threshold(joint, param)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"✅ 用例【{title}】触发异常验证成功")

@allure.feature("设置碰撞阈值")
@allure.story("设置后重启是否保存")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_collision_threshold_persistence(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    # 设置新阈值
    response = device.mc.set_collision_threshold(joint, param)

    # 重启
    device.reset()

    # 读取设置值
    get_res = device.mc.get_collision_threshold()

    # 类型断言
    assert isinstance(response, int)

    # 结果断言（eval 转换字符串列表）
    assert get_res == eval(case["l_expect_data"]), f"机械臂读取值不一致: {get_res}"

    logger.info(f"✅ 用例【{title}】测试成功")

@allure.feature("设置碰撞阈值")
@allure.story("仅上电调用 set_collision_threshold 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("发送设置碰撞阈值指令"):
        response = device.mc.set_collision_threshold(joint, param)

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置碰撞阈值")
@allure.story("下电调用 set_collision_threshold 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("发送设置碰撞阈值指令"):
        response = device.mc.set_collision_threshold(joint, param)

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

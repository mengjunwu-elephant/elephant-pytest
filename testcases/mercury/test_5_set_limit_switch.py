import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_limit_switch")


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
def teardown_go_zero(device):
    yield
    device.go_zero()


@allure.feature("限位开关设置")
@allure.story("正常设置")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_limit_switch_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"参数1: {case['parameter_1']}，参数2: {case['parameter_2']}")

    with allure.step("设置限位开关"):
        l_response = device.ml.set_limit_switch(case["parameter_1"], case["parameter_2"])
        r_response = device.mr.set_limit_switch(case["parameter_1"], case["parameter_2"])

    with allure.step("左臂断言返回类型"):
        assert isinstance(l_response, int)
    with allure.step("右臂断言返回类型"):
        assert isinstance(r_response, int)

    with allure.step("左臂断言响应结果"):
        allure.attach(str(case["l_expect_data"]),name = '左臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"],f'左臂实际值{l_response}与期望值{case["l_expect_data"]}不一致'
    with allure.step("右臂断言响应结果"):
        allure.attach(str(case["r_expect_data"]),name = '右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"],f'右臂实际值{r_response}与期望值{case["r_expect_data"]}不一致'

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("限位开关设置")
@allure.story("限位设置逻辑反馈")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "logic"], ids=lambda c: c["title"])
def test_position_feedback(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"参数1: {case['parameter_1']}，参数2: {case['parameter_2']}")

    with allure.step("设置限位开关"):
        l_response = device.ml.set_limit_switch(case["parameter_1"], case["parameter_2"])
        r_response = device.mr.set_limit_switch(case["parameter_1"], case["parameter_2"])

    with allure.step("移动关节观察限制效果"):
        l_move = device.ml.send_angle(1, 10, device.speed)
        r_move = device.mr.send_angle(1, 10, device.speed)
        sleep(2)

    with allure.step("左臂断言响应结果"):
        allure.attach(str(case["l_expect_data"]),name = '左臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_move),name = '左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_move == case["l_expect_data"],f'左臂实际值{l_move}与期望值{case["l_expect_data"]}不一致'
    with allure.step("右臂断言响应结果"):
        allure.attach(str(case["r_expect_data"]),name = '右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_move),name = '右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_move == case["r_expect_data"],f'右臂实际值{r_move}与期望值{case["r_expect_data"]}不一致'

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("限位开关设置")
@allure.story("非法参数设置 - 异常值校验")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_out_limit(device, case):
    title = case['title']
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"参数1: {case['parameter_1']}，参数2: {case['parameter_2']}")

    with allure.step(f"左臂调用 {case['api']} 异常场景接口，参数 parameter_1: {case['parameter_1']}，parameter_2: {case['parameter_2']}"):
        with pytest.raises(MercuryDataException, match='.*'):
            device.ml.set_limit_switch(case["parameter_1"], case["parameter_2"])

    with allure.step(f"右臂调用 {case['api']} 异常场景接口，参数 parameter_1: {case['parameter_1']}，parameter_2: {case['parameter_2']}"):
        with pytest.raises(MercuryDataException):
            device.mr.set_limit_switch(case["parameter_1"], case["parameter_2"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("限位开关设置")
@allure.story("限位参数是否保存")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "save_or_not"], ids=lambda c: c["title"])
def test_save_or_not(device, case):
    title = case['title']
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"参数1: {case['parameter_1']}，参数2: {case['parameter_2']}")

    with allure.step("设置限位开关参数"):
        device.ml.set_limit_switch(case["parameter_1"], case["parameter_2"])
        device.mr.set_limit_switch(case["parameter_1"], case["parameter_2"])

    with allure.step("重启机械臂"):
        device.reset()

    with allure.step("读取限位配置参数"):
        l_res = device.ml.get_limit_switch()
        r_res = device.mr.get_limit_switch()

    with allure.step("断言保存/未保存结果"):
        assert l_res == eval(case["l_expect_data"]), f"左臂限位读取值错误：{l_res}"
        assert r_res == eval(case["r_expect_data"]), f"右臂限位读取值错误：{r_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
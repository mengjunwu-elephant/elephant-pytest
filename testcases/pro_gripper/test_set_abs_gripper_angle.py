import pytest
import allure
import time
from common1 import logger
from settings import ProGripperBase
from common1.test_data_handler import get_test_data_from_excel

cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "set_abs_gripper_angle")

@pytest.fixture(scope="module")
def device():
    dev = ProGripperBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    time.sleep(3)
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_gripper(device):
    yield
    device.m.set_abs_gripper_value(0, 100)
    time.sleep(3)

@allure.feature("绝对角度设置相关接口")
@allure.story("设置绝对角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 1], ids=lambda c: c["title"])
def test_set_abs_gripper_angle(device, case):
    title = case['title']
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_value: {case["value"]}')
    with allure.step(f"调用 set_abs_gripper_value({case['value']})"):
        response = device.m.set_abs_gripper_value(case["value"])
        time.sleep(3)

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"返回类型错误，期望 int，实际为 {type(response)}"
        logger.debug("请求类型断言成功")

    with allure.step("断言返回结果符合预期"):
        allure.attach(str(case['expect_data']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际结果", attachment_type=allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"期望{case['expect_data']}，实际{response}"

    logger.info(f'请求结果断言成功，用例【{title}】测试成功')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("绝对角度设置相关接口")
@allure.story("暂停与恢复")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 2], ids=lambda c: c["title"])
def test_pause_and_resume(device, case):
    title = case['title']
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("发送绝对角度"):
        abs_res = device.m.set_abs_gripper_value(100, 1)
        time.sleep(0.5)

    with allure.step("暂停夹爪"):
        pause_res = device.m.set_gripper_pause()
        time.sleep(3)

    with allure.step("恢复夹爪"):
        resume_res = device.m.set_gripper_resume()
        time.sleep(1)

    with allure.step("断言返回类型均为 int"):
        assert all(isinstance(r, int) for r in [abs_res, pause_res, resume_res]), \
            f"返回类型错误，绝对角度返回{type(abs_res)}, 暂停返回{type(pause_res)}, 恢复返回{type(resume_res)}"
        logger.debug('请求类型断言成功')

    with allure.step("断言返回结果符合预期"):
        expect = case['expect_data']
        allure.attach(str(expect), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(f"abs_res: {abs_res}, pause_res: {pause_res}, resume_res: {resume_res}",
                      name="实际结果", attachment_type=allure.attachment_type.TEXT)
        assert abs_res == expect and pause_res == expect and resume_res == expect, \
            f"返回结果不匹配，期望：{expect}"

    logger.info(f'请求结果断言成功，用例【{title}】测试成功')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')

@allure.feature("绝对角度设置相关接口")
@allure.story("停止夹爪")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == 3], ids=lambda c: c["title"])
def test_stop(device, case):
    title = case['title']
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("发送绝对角度"):
        abs_res = device.m.set_abs_gripper_value(100, 1)
        time.sleep(0.5)

    with allure.step("停止夹爪"):
        stop_res = device.m.set_gripper_stop()

    with allure.step("断言返回类型均为 int"):
        assert all(isinstance(r, int) for r in [abs_res, stop_res]), \
            f"返回类型错误，绝对角度返回{type(abs_res)}, 停止返回{type(stop_res)}"
        logger.debug('请求类型断言成功')

    with allure.step("断言返回结果符合预期"):
        expect = case['expect_data']
        allure.attach(str(expect), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(f"abs_res: {abs_res}, stop_res: {stop_res}",
                      name="实际结果", attachment_type=allure.attachment_type.TEXT)
        assert abs_res == expect and stop_res == expect, f"返回结果不匹配，期望：{expect}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


@allure.feature("绝对角度设置相关接口")
@allure.story("异常用例验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_out_limit(device, case):
    title = case['title']
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_value: {case["value"]}')

    with allure.step("验证非法输入是否触发 ValueError"):
        with pytest.raises(ValueError, match=f".*{case['title']}.*"):
            device.m.set_abs_gripper_value(case["value"], case.get("speed", None))

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')


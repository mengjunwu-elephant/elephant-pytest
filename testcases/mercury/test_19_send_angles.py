import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryBase

# 加载 Excel 测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_angles")


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


@allure.feature("全关节角度运动")
@allure.story("正常双臂同时运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_angles_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    angles = eval(case["angles"])
    speed = case["speed"]
    logger.info(f'发送角度参数{angles}')
    logger.info(f'发送速度参数{speed}')

    with allure.step("发送 send_angles 指令到左右臂"):
        l_response = device.ml.send_angles(angles, speed,_async=True)
        device.wait()
        r_response = device.mr.send_angles(angles, speed,_async=True)
        device.wait()
        logger.info(f"左臂实际设置返回值：{l_response}")
        logger.info(f"右臂实际设置返回值：{r_response}")

    with allure.step('调用 get_angles 接口'):
        l_get_res = device.ml.get_angles()
        r_get_res = device.mr.get_angles()
        logger.info(f'左臂实际读取返回值：{l_get_res}')
        logger.info(f'右臂实际读取返回值：{r_get_res}')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误: {type(r_response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="左臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(case["r_expect_data"]), name="右臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response), name="右臂实际", attachment_type=allure.attachment_type.TEXT)

        assert_almost_equal(l_response,case["l_expect_data"],tol=1,name='左臂全关节运动'), f"左臂响应不一致，期望: {case['l_expect_data']}，实际: {l_response}"
        assert_almost_equal(r_response,case["r_expect_data"],tol=1,name='右臂全关节运动'), f"右臂响应不一致，期望: {case['r_expect_data']}，实际: {r_response}"

    with allure.step('断言 get_angles 接口返回值是否匹配预期'):
        allure.attach(str(angles), name="左臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_get_res), name="左臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(angles), name="右臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_get_res), name="右臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(l_get_res,angles,tol=1,name='左臂全关节运动'), f"左臂响应不一致，期望: {angles}，实际: {l_get_res}"
        assert_almost_equal(r_get_res,angles,tol=1,name='右臂全关节运动'), f"右臂响应不一致，期望: {angles}，实际: {r_get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("全关节角度运动")
@allure.story("左臂全关节运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "left"], ids=lambda c: c["title"])
def test_send_angles_left(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    angles = eval(case["angles"])
    speed = case["speed"]
    logger.info(f'发送角度参数：{angles}')
    logger.info(f'速度参数：{speed}')

    with allure.step("发送 send_angles 指令到左臂"):
        l_response = device.ml.send_angles(angles, speed)
        device.wait()
        logger.info(f"左臂实际设置返回值：{l_response}")

    with allure.step('调用 get_angles 接口'):
        l_get_res = device.ml.get_angles()
        logger.info(f'左臂实际读取返回值：{l_get_res}')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="左臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == l_response, f"左臂响应不一致，期望: {case['l_expect_data']}，实际: {l_response}"

    with allure.step('断言 get_angles 接口返回值是否匹配预期'):
        allure.attach(str(angles), name="左臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_get_res), name="左臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(l_get_res,angles,tol=1,name='左臂全关节运动'), f"左臂响应不一致，期望: {angles}，实际: {l_get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("全关节角度运动")
@allure.story("右臂全关节运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "right"], ids=lambda c: c["title"])
def test_send_angles_right(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    angles = eval(case["angles"])
    speed = case["speed"]
    logger.info(f'发送角度参数：{angles}')
    logger.info(f'速度参数：{speed}')

    with allure.step("发送 send_angles 指令到右臂"):
        r_response = device.mr.send_angles(angles, speed)
        device.wait()
        logger.info(f"右臂实际设置返回值：{r_response}")

    with allure.step('调用 get_angles 接口'):
        r_get_res = device.mr.get_angles()
        logger.info(f'右臂实际读取返回值：{r_get_res}')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(r_response, int), f"左臂返回类型错误: {type(r_response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["r_expect_data"]), name="右臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response), name="右臂实际", attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂响应不一致，期望: {case['r_expect_data']}，实际: {r_response}"

    with allure.step('断言 get_angles 接口返回值是否匹配预期'):
        allure.attach(str(angles), name="右臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_get_res), name="右臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(r_get_res,angles,tol=1,name='右臂全关节运动'), f"右臂响应不一致，期望: {angles}，实际: {r_response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("发送角度指令")
@allure.story("异常角度发送触发异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_angles_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    angles = eval(case["angles"])
    speed = case["speed"]
    logger.info(f'发送角度参数：{angles}')
    logger.info(f'速度参数：{speed}')

    with allure.step("尝试发送非法角度并期望抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.ml.send_angles(angles, speed)
            device.mr.send_angles(angles, speed)

    allure.attach(str(angles), name="发送角度参数", attachment_type=allure.attachment_type.TEXT)
    allure.attach(str(speed), name="速度参数", attachment_type=allure.attachment_type.TEXT)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

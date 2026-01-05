import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_coords")

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

@pytest.fixture(autouse=True)
def init_coords(device):
    device.init_coords()


@allure.feature("设置全坐标")
@allure.story("正常路径测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_coords(device, case):
    allure.dynamic.title(case["title"])
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")

    param = eval(case["parameter"])
    speed = case["speed"]

    with allure.step("左臂发送坐标"):
        l_response = device.ml.send_coords(param, speed)
        logger.debug(f"左臂返回值：{l_response}")

    with allure.step("右臂发送坐标"):
        r_response = device.mr.send_coords(param, speed)
        logger.debug(f"右臂返回值：{r_response}")

    with allure.step("获取双臂坐标"):
        l_get_res = device.ml.get_coords()
        r_get_res = device.mr.get_coords()
        logger.debug(f"左臂获取坐标：{l_get_res}")
        logger.debug(f"右臂获取坐标：{r_get_res}")

    with allure.step('断言返回类型'):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert l_response == case["l_expect_data"], f"左臂期望值：{case['l_expect_data']}，实际值：{l_response}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        assert r_response == case["r_expect_data"], f"右臂期望值：{case['r_expect_data']}，实际值：{r_response}"

    with allure.step('断言 get_coords 接口返回值是否匹配预期'):
        allure.attach(str(case['l_expect_data']), name="左臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_get_res), name="左臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(case['r_expect_data']), name="右臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_get_res), name="右臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(l_get_res,eval(case['l_expect_data']),tol=3,name='左臂发送全坐标'), f"左臂响应不一致，期望: {case['l_expect_data']}，实际: {l_get_res}"
        assert_almost_equal(r_get_res,eval(case['r_expect_data']),tol=3,name='右臂发送全坐标'), f"右臂响应不一致，期望: {case['r_expect_data']}，实际: {r_get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")


@allure.feature("send_coords 接口测试")
@allure.story("左臂边界与异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") in {"exception", "left"}], ids=lambda c: c["title"])
def test_send_coords_out_limit_left(device, case):
    allure.dynamic.title(f"[左臂] {case['title']}")
    param = eval(case["parameter"])
    speed = case["speed"]

    logger.info(f"》》》》》用例【{case['title']}】开始测试（左臂）《《《《《")
    with allure.step("左臂发送非法坐标，断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.send_coords(param, speed)

    logger.info(f"✅ 用例【{case['title']}】左臂异常验证成功")


@allure.feature("send_coords 接口测试")
@allure.story("右臂边界与异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") in {"exception", "right"}], ids=lambda c: c["title"])
def test_send_coords_out_limit_right(device, case):
    allure.dynamic.title(f"[右臂] {case['title']}")
    param = eval(case["parameter"])
    speed = case["speed"]

    logger.info(f"》》》》》用例【{case['title']}】开始测试（右臂）《《《《《")
    with allure.step("右臂发送非法坐标，断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.mr.send_coords(param, speed)

    logger.info(f"✅ 用例【{case['title']}】右臂异常验证成功")

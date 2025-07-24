import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_coord")


@pytest.fixture(scope="module")
def device():
    """初始化设备，仅模块级一次"""
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("设备初始化完成")
    yield dev
    dev.go_zero()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("设备已关闭")


@pytest.fixture(autouse=True)
def reset_coords(device):
    """每个用例前初始化坐标"""
    device.init_coords()


@allure.feature("send_coord 接口")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_coord_normal(device, case):
    allure.dynamic.title(case["title"])
    logger.info(f"【开始测试】：{case['title']}")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    with allure.step("左臂发送坐标"):
        l_resp = device.ml.send_coord(axis, param, speed)
        logger.debug(f"左臂返回：{l_resp}")
        assert isinstance(l_resp, int), f"左臂返回类型错误，应为 int，实际为 {type(l_resp)}"
        assert l_resp == case["l_expect_data"], f"左臂预期 {case['l_expect_data']}，实际 {l_resp}"

    with allure.step("右臂发送坐标"):
        r_resp = device.mr.send_coord(axis, param, speed)
        logger.debug(f"右臂返回：{r_resp}")
        assert isinstance(r_resp, int), f"右臂返回类型错误，应为 int，实际为 {type(r_resp)}"
        assert r_resp == case["r_expect_data"], f"右臂预期 {case['r_expect_data']}，实际 {r_resp}"

    logger.info(f"✅ 用例【{case['title']}】通过")


@allure.feature("send_coord 接口")
@allure.story("异常用例 - 左臂")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") in {"exception", "left"}],
                         ids=lambda c: c["title"])
def test_send_coord_left_exception(device, case):
    allure.dynamic.title(f"[左臂异常] {case['title']}")
    logger.info(f"【开始测试 - 左臂异常】：{case['title']}")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    with allure.step("发送非法坐标参数至左臂"):
        with pytest.raises(MercuryDataException):
            device.ml.send_coord(axis, param, speed)
    logger.info(f"✅ 左臂异常用例【{case['title']}】验证通过")


@allure.feature("send_coord 接口")
@allure.story("异常用例 - 右臂")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") in {"exception", "right"}],
                         ids=lambda c: c["title"])
def test_send_coord_right_exception(device, case):
    allure.dynamic.title(f"[右臂异常] {case['title']}")
    logger.info(f"【开始测试 - 右臂异常】：{case['title']}")

    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]

    with allure.step("发送非法坐标参数至右臂"):
        with pytest.raises(MercuryDataException):
            device.mr.send_coord(axis, param, speed)
    logger.info(f"✅ 右臂异常用例【{case['title']}】验证通过")

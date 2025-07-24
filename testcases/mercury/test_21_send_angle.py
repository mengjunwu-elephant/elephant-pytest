import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_angle")


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
def reset_position(device):
    yield
    # 用于用例间复位右臂角度
    device.go_zero()
    device.mr.send_angle(11, 0, 50)
    device.mr.send_angle(12, 0, 50)
    device.mr.send_angle(13, 0, 50)


@allure.feature("send_angle 左臂测试")
@allure.story("左臂发送角度 - 正常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_angle_left(device, case):
    with allure.step(f"发送左臂角度指令 - 关节: {case['joint']}，角度: {case['parameter']}，速度: {case['speed']}"):
        response = device.ml.send_angle(case['joint'], case["parameter"], case["speed"])

    with allure.step("断言返回类型和预期值"):
        assert isinstance(response, int), f"左臂返回类型错误：{type(response)}"
        assert response == case["l_expect_data"], f"左臂返回值不一致，期望 {case['l_expect_data']}，实际 {response}"

    logger.info(f"✅ 用例【{case['title']}】左臂测试通过")


@allure.feature("send_angle 右臂测试")
@allure.story("右臂发送角度 - 正常和部分独立场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") in {"normal", "right"}], ids=lambda c: c["title"])
def test_send_angle_right(device, case):
    with allure.step(f"发送右臂角度指令 - 关节: {case['joint']}，角度: {case['parameter']}，速度: {case['speed']}"):
        response = device.mr.send_angle(case['joint'], case["parameter"], case["speed"])

    with allure.step("断言返回类型和预期值"):
        assert isinstance(response, int), f"右臂返回类型错误：{type(response)}"
        assert response == case["r_expect_data"], f"右臂返回值不一致，期望 {case['r_expect_data']}，实际 {response}"

    logger.info(f"✅ 用例【{case['title']}】右臂测试通过")


@allure.feature("send_angle 异常测试")
@allure.story("无效角度或速度触发异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_angle_out_of_limit(device, case):
    with allure.step("尝试使用非法 joint/angle/speed 参数"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.ml.send_angle(case['joint'], case["parameter"], case["speed"])
            device.mr.send_angle(case['joint'], case["parameter"], case["speed"])

    allure.attach(str(case["joint"]), name="关节号", attachment_type=allure.attachment_type.TEXT)
    allure.attach(str(case["parameter"]), name="角度参数", attachment_type=allure.attachment_type.TEXT)
    allure.attach(str(case["speed"]), name="速度参数", attachment_type=allure.attachment_type.TEXT)
    logger.info(f"✅ 用例【{case['title']}】成功触发异常：{exc_info.value}")

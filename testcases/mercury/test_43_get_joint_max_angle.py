import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从 Excel 加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_joint_max_angle")


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
def restore_zero(device):
    # 每个用例后清理
    yield
    device.go_zero()
    sleep(3)


@allure.feature("获取关节最大角度")
@allure.story("正常用例 - 到达角度 + 返回值断言")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_joint_max_angle_normal(device, case):
    title = case["title"]
    joint_id = case["id"]
    l_expect = case["l_expect_data"]
    r_expect = case["r_expect_data"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("获取左右臂最大角度"):
        l_response = device.ml.get_joint_max_angle(joint_id)
        r_response = device.mr.get_joint_max_angle(joint_id)

    with allure.step("发送最大角度指令"):
        device.ml.send_angle(joint_id, l_expect, device.speed)
        device.mr.send_angle(joint_id, r_expect, device.speed)
        sleep(3)

    with allure.step("判断是否到达预期角度"):
        l_curr = device.ml.get_angle(joint_id)
        r_curr = device.mr.get_angle(joint_id)
        l_ok = device.is_in_position(l_expect, l_curr)
        r_ok = device.is_in_position(r_expect, r_curr)

        assert l_ok == 1, f"左臂 {joint_id} 未到达最大角度：目标={l_expect}, 当前={l_curr}"
        assert r_ok == 1, f"右臂 {joint_id} 未到达最大角度：目标={r_expect}, 当前={r_curr}"

    with allure.step("断言返回值正确"):
        assert isinstance(l_response, float), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, float), f"右臂返回类型错误：{type(r_response)}"
        assert l_response == l_expect, f"左臂最大角断言失败：期望={l_expect}, 实际={l_response}"
        assert r_response == r_expect, f"右臂最大角断言失败：期望={r_expect}, 实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("获取关节最大角度")
@allure.story("异常用例 - 越界 ID 报错验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_joint_max_angle_exception(device, case):
    title = case["title"]
    joint_id = case["id"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("断言非法 ID 抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.get_joint_max_angle(joint_id)
            device.mr.get_joint_max_angle(joint_id)

    logger.info(f"✅ 异常断言成功，用例【{title}】通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

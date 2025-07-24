import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_joint_max_angle")


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
    yield
    device.go_zero()
    sleep(3)


@allure.feature("设置关节最大角度")
@allure.story("正常用例 - 限位设置后能到达 + 返回值正确")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_joint_max_angle_normal(device, case):
    title = case["title"]
    joint_id = case["id"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("设置最大角度 + 执行运动指令"):
        l_response = device.ml.set_joint_max_angle(param)
        r_response = device.mr.set_joint_max_angle(param)

        device.ml.send_angle(joint_id, param, device.speed)
        device.mr.send_angle(joint_id, param, device.speed)
        sleep(3)

    with allure.step("判断是否到达目标角度"):
        l_curr = device.ml.get_angle(joint_id)
        r_curr = device.mr.get_angle(joint_id)
        assert device.is_in_position(param, l_curr), f"左臂未到达最大角度，当前={l_curr}, 目标={param}"
        assert device.is_in_position(param, r_curr), f"右臂未到达最大角度，当前={r_curr}, 目标={param}"

    with allure.step("断言类型和返回数据一致"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        assert l_response == case["l_expect_data"], f"左臂返回错误：期望={case['l_expect_data']}, 实际={l_response}"
        assert r_response == case["r_expect_data"], f"右臂返回错误：期望={case['r_expect_data']}, 实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置关节最大角度")
@allure.story("异常用例 - 设置非法角度抛出异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_joint_max_angle_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("断言设置非法角度抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.set_joint_max_angle(param)
        with pytest.raises(MercuryDataException):
            device.mr.set_joint_max_angle(param)

    logger.info(f"✅ 异常用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置关节最大角度")
@allure.story("设置是否保存 - 重启后验证限位值是否保留")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_joint_max_angle_save_or_not(device, case):
    title = case["title"]
    joint_id = case["id"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("设置最大角度"):
        l_response = device.ml.set_joint_max_angle(joint_id, param)
        r_response = device.mr.set_joint_max_angle(joint_id, param)

    with allure.step("设备重启"):
        device.reset()

    with allure.step("读取重启后的最大角度值"):
        l_actual = device.ml.get_joint_max_angle(joint_id)
        r_actual = device.mr.get_joint_max_angle(joint_id)

    with allure.step("断言值是否保存"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        assert l_actual == case["l_expect_data"], f"左臂最大角度未正确保存：期望={case['l_expect_data']}, 实际={l_actual}"
        assert r_actual == case["r_expect_data"], f"右臂最大角度未正确保存：期望={case['r_expect_data']}, 实际={r_actual}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
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
@allure.story("左臂正常用例 - 限位设置后能到达 + 返回值正确")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_joint_max_angle_left(device, case):
    title = case["title"]
    joint_id = case["id"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("设置最大角度 + 执行运动指令"):
        l_response = device.ml.set_joint_max_angle(joint_id,param)

        device.ml.send_angle(joint_id, param+5, device.speed)
        sleep(3)

    with allure.step("判断是否到达目标角度"):
        l_curr = device.ml.get_angle(joint_id)
        assert_almost_equal(l_curr, param, 1,name='设置关节最大角度'), f"左臂返回错误：期望={param}, 实际={l_curr}"

    with allure.step("断言类型和返回数据一致"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert l_response == case["l_expect_data"], f"左臂返回错误：期望={case['l_expect_data']}, 实际={l_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置关节最大角度")
@allure.story("右臂正常用例 - 限位设置后能到达 + 返回值正确")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_joint_max_angle_right(device, case):
    title = case["title"]
    joint_id = case["id"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("设置最大角度 + 执行运动指令"):
        r_response = device.mr.set_joint_max_angle(joint_id,param)
        device.mr.send_angle(joint_id, param+5, device.speed)
        sleep(3)

    with allure.step("判断是否到达目标角度"):
        r_curr = device.mr.get_angle(joint_id)
        assert_almost_equal(r_curr,param,tol=1,name='设置关节最大角度'), f"右臂返回错误：期望={param}, 实际={r_curr}"

    with allure.step("断言类型和返回数据一致"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        assert r_response == case["r_expect_data"], f"右臂返回错误：期望={case['r_expect_data']}, 实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置关节最大角度")
@allure.story("异常用例 - 设置非法角度抛出异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_joint_max_angle_exception(device, case):
    title = case["title"]
    param = case["parameter"]
    joint = case["id"]

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("断言设置非法角度抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.set_joint_max_angle(joint,param)
            device.mr.set_joint_max_angle(joint,param)

    logger.info(f"✅ 异常用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


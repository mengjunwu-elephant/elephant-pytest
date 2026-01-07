import pytest
import allure
from time import sleep
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载 Excel 测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_joint_min_angle")


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


@allure.feature("设置关节最小角度")
@allure.story("正常用例 - 限位设置后能到达 + 返回值正确")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_joint_min_angle_normal(device, case):
    title = case['title']
    joint_id = case['id']
    param = case['parameter']

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("设置最小角度 + 执行运动指令"):
        l_response = device.ml.set_joint_min_angle(joint_id,param)
        device.ml.send_angle(joint_id, param-5, device.speed)

        r_response = device.mr.set_joint_min_angle(joint_id,param)
        device.mr.send_angle(joint_id, param-5, device.speed)

        sleep(3)

    with allure.step("判断是否到达软件限位"):
        l_curr = device.ml.get_angle(joint_id)
        r_curr = device.mr.get_angle(joint_id)
        assert_almost_equal(l_curr, param, 1), f"左臂未到达软件限位：期望={param}, 实际={l_curr}"
        assert_almost_equal(r_curr, param, 1), f"右臂未到达软件限位：期望={param}, 实际={r_curr}"

    with allure.step("断言返回类型和数据正确"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        assert l_response == case['l_expect_data'], f"左臂返回数据错误：期望={case['l_expect_data']}, 实际={l_response}"
        assert r_response == case['r_expect_data'], f"右臂返回数据错误：期望={case['r_expect_data']}, 实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置关节最小角度")
@allure.story("异常用例 - 设置非法角度抛出异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_joint_min_angle_exception(device, case):
    title = case['title']
    param = case['parameter']

    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("断言左右臂均抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.set_joint_min_angle(param)
            device.mr.set_joint_min_angle(param)

    logger.info(f"✅ 异常用例【{title}】通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


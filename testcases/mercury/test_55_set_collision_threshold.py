import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_collision_threshold")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 恢复默认阈值
    for i in range(7):
        dev.ml.set_collision_threshold(i + 1, 100)
        dev.mr.set_collision_threshold(i + 1, 100)
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置碰撞阈值")
@allure.story("正常设置碰撞阈值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_collision_threshold_normal(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    l_response = device.ml.set_collision_threshold(joint, param)
    r_response = device.mr.set_collision_threshold(joint, param)

    assert isinstance(l_response, int), f"左臂响应类型错误: {type(l_response)}"
    assert isinstance(r_response, int), f"右臂响应类型错误: {type(r_response)}"

    assert l_response == case["l_expect_data"], f"左臂响应错误: 期望={case['l_expect_data']}, 实际={l_response}"
    assert r_response == case["r_expect_data"], f"右臂响应错误: 期望={case['r_expect_data']}, 实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")


@allure.feature("设置碰撞阈值")
@allure.story("异常设置 - 越界/非法参数应抛异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_collision_threshold_exception(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    with pytest.raises(MercuryDataException):
        device.ml.set_collision_threshold(joint, param)
    with pytest.raises(MercuryDataException):
        device.mr.set_collision_threshold(joint, param)

    logger.info(f"✅ 用例【{title}】触发异常验证成功")


@allure.feature("设置碰撞阈值")
@allure.story("设置后重启是否保存")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_collision_threshold_persistence(device, case):
    joint = case["joint"]
    param = case["parameter"]
    title = case["title"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: joint={joint}, param={param}")

    # 设置新阈值
    l_response = device.ml.set_collision_threshold(joint, param)
    r_response = device.mr.set_collision_threshold(joint, param)

    # 重启
    device.reset()

    # 读取设置值
    l_get_res = device.ml.get_collision_threshold()
    r_get_res = device.mr.get_collision_threshold()

    # 类型断言
    assert isinstance(l_response, int)
    assert isinstance(r_response, int)

    # 结果断言（eval 转换字符串列表）
    assert l_get_res == eval(case["l_expect_data"]), f"左臂读取值不一致: {l_get_res}"
    assert r_get_res == eval(case["r_expect_data"]), f"右臂读取值不一致: {r_get_res}"

    logger.info(f"✅ 用例【{title}】测试成功")

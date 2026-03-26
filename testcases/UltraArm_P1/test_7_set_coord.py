import time
from typing import Any

import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import UltraArmP1Base

# 从 Excel 读取测试数据（含 test_type=step_repeat 时必填列 step / repeat_count / tol）
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_coord")


def _coord_axis_index(axis: str) -> int:
    m = {"X": 0, "Y": 1, "Z": 2, "R": 3}
    key = str(axis).upper()
    if key not in m:
        raise ValueError(f"不支持的坐标轴: {axis!r}")
    return m[key]


def _read_coord(mc: Any, axis: str) -> float:
    return float(mc.get_coords_info()[_coord_axis_index(axis)])


def _sr_int(case: dict[str, Any], key: str, default: int) -> int:
    v = case.get(key)
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return default
    return int(v)


def _sr_float(case: dict[str, Any], key: str, default: float) -> float:
    v = case.get(key)
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return default
    return float(v)


def run_set_coord_step_repeat(device: UltraArmP1Base, case: dict[str, Any]) -> tuple[Any, float, float, float]:
    """
    先到 coords_init，再沿 axis 连续 repeat_count 次 set_coord，目标为 initial + i*step。
    返回 (最后一次接口返回值, 理论终点, 读回终点, 容差 mm)。
    """
    axis = str(case["axis"]).upper()
    step = float(case["step"])
    n = _sr_int(case, "repeat_count", 10)
    tol = _sr_float(case, "tol", 0.1)
    speed = int(case["speed"])

    device.mc.set_angles(device.coords_init_angles, device.speed)
    device.wait()
    init = _read_coord(device.mc, axis)
    last_set: Any = None
    for i in range(1, n + 1):
        target = init + i * step
        last_set = device.mc.set_coord(axis, target, speed)
        device.wait()
    final = _read_coord(device.mc, axis)
    expected = init + n * step
    return last_set, expected, final, tol


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理（teardown 回零位）"""
    dev = UltraArmP1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置单坐标")
@allure.story("设置单坐标")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_send_coord0(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'axis:{case["axis"]}')
    logger.debug(f'coord:{case["coord"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step('使机械臂运动到坐标初始位置'):
        device.mc.set_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_coord(case["axis"],case["coord"],case["speed"])
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step(f'调用 get_coords 接口'):
        if case["axis"] == 'X':
            get_res = device.mc.get_coords_info()[0]
        elif case["axis"] == 'Y':
            get_res = device.mc.get_coords_info()[1]
        elif case["axis"] == 'Z':
            get_res = device.mc.get_coords_info()[2]
        elif case["axis"] == 'R':
            get_res = device.mc.get_coords_info()[3]
        logger.debug(f"接口返回：{get_res}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(set_res, str), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言 get_coords 返回值"):
        allure.attach(str(case["coord"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, case["coord"], 2,'设置单坐标'), f"用例【{title}】断言失败，期望 {case['coord']},实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置单坐标")
@allure.story("超限报错验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_coord_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'axis:{case["axis"]}')
    logger.debug(f'coord:{case["coord"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step(f"断言抛出 ultraArmP1DataException,笛卡尔积坐标系为{case['axis']},坐标值为{case['coord']}, 速度为{case['speed']}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_coord(case["axis"],case["coord"], case["speed"])

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置单坐标")
@allure.story("多步累积 set_coord（Excel test_type=step_repeat）")
@pytest.mark.slow
@pytest.mark.parametrize("case", [c for c in cases if (c.get("test_type") or "").strip() == "step_repeat"], ids=lambda c: c["title"])
def test_send_coord_step_repeat(device, case):
    title = case["title"]
    expected_ret = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'axis:{case["axis"]}')
    logger.debug(f'step:{case["step"]}')
    logger.debug(f'repeat_count:{case["repeat_count"]}')
    logger.debug(f'tol:{case["tol"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step("连续 set_coord 共 repeat_count 次，终点相对初始累积 n*step"):
        set_res, exp_final, read_final, tol = run_set_coord_step_repeat(device, case)
        logger.debug(f"接口返回：{set_res} 理论终点={exp_final} 读回={read_final}")

    with allure.step("断言最后一次接口返回"):
        assert isinstance(set_res, str), f"返回类型错误,应为 str,实际为 {type(set_res)}"
        assert set_res == expected_ret, f"用例【{title}】期望 {expected_ret},实际 {set_res}"

    with allure.step(f"断言读回坐标在 ±{tol}mm 内"):
        assert_almost_equal(read_final, exp_final, tol, "多步累积 set_coord 终点")

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

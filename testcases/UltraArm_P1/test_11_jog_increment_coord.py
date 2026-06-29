# -*- coding: utf-8 -*-
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "jog_increment_coord")

_AXIS_NAMES = ("X", "Y", "Z", "Rx")


def _goto_coords_init(device: UltraArmP1Base) -> None:
    device.mc.set_angles(device.coords_init_angles, device.speed)
    device.wait()


@allure.feature("坐标步进模式")
@allure.story("初始点位四轴步进±20mm")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_jog_increment_coord0(device, case):
    title = case["title"]
    expected = case["expect_data"]
    axis = int(case["axis"])
    increment = float(case["increment"])
    speed = int(case["speed"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'axis:{case["axis"]}')
    logger.debug(f'increment:{case["increment"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step("运动到坐标初始点位"):
        _goto_coords_init(device)

    with allure.step("读取步进前坐标"):
        init_coord = float(device.mc.get_coords_info()[axis - 1])
        logger.debug(f"步进前 {_AXIS_NAMES[axis - 1]}={init_coord}")

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.jog_increment_coord(axis, increment, speed)
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step("读取步进后坐标"):
        final_coord = float(device.mc.get_coords_info()[axis - 1])
        logger.debug(f"步进后 {_AXIS_NAMES[axis - 1]}={final_coord}")

    with allure.step("断言接口返回 ok"):
        assert isinstance(set_res, str), f"返回类型错误,应为 str,实际为 {type(set_res)}"
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    expected_coord = init_coord + increment
    with allure.step(f"断言 {_AXIS_NAMES[axis - 1]} 轴读回坐标相对初始增量 {increment}mm"):
        allure.attach(str(expected_coord), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(final_coord), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(
            final_coord,
            expected_coord,
            2,
            "jog_increment_coord 步进读回",
        ), f"用例【{title}】断言失败，期望 {expected_coord},实际 {final_coord}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("坐标步进模式")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_jog_increment_coord_exception(device, case):
    title = case["title"]
    axis = int(case["axis"])
    increment = float(case["increment"])
    speed = int(case["speed"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'axis:{case["axis"]}')
    logger.debug(f'increment:{case["increment"]}')
    logger.debug(f'speed:{case["speed"]}')

    with allure.step("运动到坐标初始点位"):
        _goto_coords_init(device)

    with allure.step(
        f"断言抛出 ultraArmP1DataException,轴={axis},增量={increment},速度={speed}"
    ):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.jog_increment_coord(axis, increment, speed)

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

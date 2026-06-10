# -*- coding: utf-8 -*-
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_collision_threshold")


@allure.feature("设置碰撞阈值")
@allure.story("正确设置碰撞阈值")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_collision_threshold(device, case):
    title = case["title"]
    expected = case["expect_data"]
    joint_id = case["joint_id"]
    threshold = case["threshold"]
    restore_threshold = case["restore_threshold"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint_id:{joint_id}')
    logger.debug(f'threshold:{threshold}')
    logger.debug(f'restore_threshold:{restore_threshold}')

    try:
        with allure.step(f"调用 {case['api']} 接口"):
            set_res = device.mc.set_collision_threshold(joint_id, threshold)
            logger.debug(f"接口返回：{set_res}")

        with allure.step("调用 get_collision_threshold 接口"):
            get_res = device.mc.get_collision_threshold()
            logger.debug(f"接口返回：{get_res}")

        with allure.step("断言 set_collision_threshold 返回值"):
            allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
            allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
            assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

        with allure.step("断言碰撞阈值已设置成功"):
            if joint_id == 0:
                assert all(v == threshold for v in get_res), (
                    f"用例【{title}】断言失败，期望全部为 {threshold}，实际 {get_res}"
                )
            else:
                actual = get_res[joint_id - 1]
                allure.attach(str(threshold), name="期望值", attachment_type=allure.attachment_type.TEXT)
                allure.attach(str(actual), name="实际值", attachment_type=allure.attachment_type.TEXT)
                assert actual == threshold, f"用例【{title}】断言失败，期望 {threshold}，实际 {actual}"

        logger.info(f'✅ 用例【{title}】测试通过')
    finally:
        if restore_threshold is not None:
            with allure.step(f"恢复碰撞阈值为 {restore_threshold}"):
                device.mc.set_collision_threshold(joint_id, restore_threshold)
                logger.debug(f"已恢复 joint_id={joint_id} threshold={restore_threshold}")

    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置碰撞阈值")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_collision_threshold_exception(device, case):
    title = case["title"]
    joint_id = case["joint_id"]
    threshold = case["threshold"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint_id:{joint_id}')
    logger.debug(f'threshold:{threshold}')

    with allure.step(f"断言抛出 ultraArmP1DataException，关节为 {joint_id}，阈值为 {threshold}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_collision_threshold(joint_id, threshold)

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

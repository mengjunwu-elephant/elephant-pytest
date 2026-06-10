# -*- coding: utf-8 -*-
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_robot_id")


@allure.feature("设置机器码")
@allure.story("正确设置机器码")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_robot_id(device, case):
    title = case["title"]
    expected = case["expect_data"]
    robot_id = case["robot_id"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'robot_id:{robot_id}')

    original_id = device.mc.get_robot_id()
    logger.debug(f'original_robot_id:{original_id}')

    try:
        with allure.step("读取原始机器码"):
            allure.attach(str(original_id), name="原始机器码", attachment_type=allure.attachment_type.TEXT)

        with allure.step(f"调用 {case['api']} 接口"):
            set_res = device.mc.set_robot_id(robot_id)
            logger.debug(f"接口返回：{set_res}")

        with allure.step("调用 get_robot_id 验证"):
            get_res = device.mc.get_robot_id()
            logger.debug(f"接口返回：{get_res}")

        with allure.step("断言 set_robot_id 返回值"):
            allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
            allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
            assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

        with allure.step("断言机器码已设置成功"):
            allure.attach(str(robot_id), name="期望值", attachment_type=allure.attachment_type.TEXT)
            allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
            assert get_res == robot_id, f"用例【{title}】断言失败，期望 {robot_id}，实际 {get_res}"

        logger.info(f'✅ 用例【{title}】测试通过')
    finally:
        with allure.step(f"恢复原始机器码 {original_id}"):
            device.mc.set_robot_id(original_id)
            logger.debug(f"已恢复 robot_id={original_id}")

    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

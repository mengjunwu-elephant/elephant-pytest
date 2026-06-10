# -*- coding: utf-8 -*-
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "get_collision_threshold")


@allure.feature("获取碰撞阈值")
@allure.story("正确获取碰撞阈值")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_collision_threshold(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.get_collision_threshold()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误，应为 list，实际为 {type(response)}"

    with allure.step("断言列表长度为 4"):
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert len(response) == 4, f"用例【{title}】断言失败，期望长度 4，实际 {len(response)}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

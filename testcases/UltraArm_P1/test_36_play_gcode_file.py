# -*- coding: utf-8 -*-
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "play_gcode_file")

@allure.feature("轨迹播放")
@allure.story("播放SD卡中的Gcode轨迹文件")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_play_gcode_file(device, case):
    title = case["title"]
    filename = case["filename"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'filename:{filename}')

    # with allure.step("确认 SD 卡中已有 Gcode 轨迹文件"):
    #     input(f"请确认 SD 卡中已存在轨迹文件 {filename}，按回车键继续测试")

    with allure.step(f"调用 play_gcode_file({filename}) 接口"):
        device.mc.play_gcode_file(filename)
        logger.debug("play_gcode_file 已调用，等待运动结束")

    with allure.step("等待轨迹播放完成"):
        device.wait()

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

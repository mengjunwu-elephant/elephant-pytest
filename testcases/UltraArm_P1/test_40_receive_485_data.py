# -*- coding: utf-8 -*-
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "receive_485_data")

pytestmark = pytest.mark.peripheral


@allure.feature("485通信")
@allure.story("接收485数据")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_receive_485_data(device, case):
    if not hasattr(device.mc, "receive_485_data"):
        pytest.skip("当前 pymycobot 版本不支持 receive_485_data")

    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("确认 485 通信环境已就绪"):
        input("请确认 485 通信环境已连接并准备好发送数据，按回车键继续测试")

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.receive_485_data()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言接口返回结果"):
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response is not None, f"用例【{title}】断言失败，receive_485_data 返回 None"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

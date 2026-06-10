# -*- coding: utf-8 -*-
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_wifi_password")


@allure.feature("WiFi配置")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_wifi_password_exception(device, case):
    title = case["title"]
    wifi_name = case["wifi_name"]
    password = case["password"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'wifi_name:{wifi_name}')
    logger.debug(f'password:{password}')

    with allure.step(f"断言抛出 ultraArmP1DataException，WiFi 名称为 {wifi_name}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_wifi_password(wifi_name, password)

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

# -*- coding: utf-8 -*-
import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_wifi_password")


@pytest.fixture(scope="module", autouse=True)
def confirm_wifi_ap_ready(device):
    prompt_continue("请确认机械臂已切换为 WLAN 模式且 WiFi 环境就绪，按回车继续")
    yield


@allure.feature("WiFi配置")
@allure.story("正常设置WiFi密码")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_wifi_password_normal(device, case):
    title = case["title"]
    wifi_name = case["wifi_name"]
    password = case["password"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'wifi_name:{wifi_name}')
    logger.debug(f'password:{password}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_wifi_password(wifi_name, password)
        logger.debug(f"接口返回：{response}")

    with allure.step("断言接口返回成功"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        if str(expected).lower() == "ok":
            assert str(response).lower() in ("ok", "1"), (
                f"用例【{title}】断言失败，期望 ok，实际 {response!r}"
            )
        else:
            assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


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


@allure.feature("WiFi配置")
@allure.story("设备返回错误")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception_device"], ids=lambda c: c["title"])
def test_set_wifi_password_device_error(device, case):
    title = case["title"]
    wifi_name = case["wifi_name"]
    password = case["password"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'wifi_name:{wifi_name}')
    logger.debug(f'password:{password}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_wifi_password(wifi_name, password)
        logger.debug(f"接口返回：{response}")

    with allure.step("断言设备返回错误提示"):
        allure.attach(str(expected), name="期望包含", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert str(response).lower() != "ok", f"用例【{title}】断言失败，不应返回 ok，实际 {response!r}"
        assert expected in str(response), f"用例【{title}】断言失败，期望包含 {expected!r}，实际 {response!r}"

    logger.info(f"✅ 用例【{title}】异常断言通过,返回信息：{response}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

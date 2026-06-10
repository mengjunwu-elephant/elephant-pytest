import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_coords_max_speed")


@allure.feature("最大速度坐标运动")
@allure.story("正确设置最大速度坐标运动")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_coords_max_speed0(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'coords:{case["coords"]}')

    with allure.step(f"调整机械臂角度，避免耦合"):
        device.mc.set_angles(device.coords_init_angles, device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.set_coords_max_speed(eval(case["coords"]))
        device.wait()
        logger.debug(f"接口返回：{set_res}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(set_res, str), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_enable")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()  # 实例化夹爪
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置夹爪使能-正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])
def test_set_gripper_enable(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameters:{case["parameter"]}')

    set_res = device.m.set_gripper_enable(case["parameter"])

    assert isinstance(set_res, int), f"请求类型断言失败，实际类型为{type(set_res)}"
    assert set_res == case['expect_data'], f"请求结果断言失败，期望：{case['expect_data']}，实际：{set_res}"

    logger.info(f'请求结果断言成功，用例【{case["title"]}】测试成功')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置夹爪使能-异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_enable_exception(device, case):
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_parameters:{case["parameter"]}')

    with pytest.raises(ValueError, match=f".*{case['title']}.*"):
        device.m.set_gripper_enable(int(case['parameter']))

    logger.info(f'请求结果断言成功，用例【{case["title"]}】测试成功')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

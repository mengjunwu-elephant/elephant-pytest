import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_angles")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取角度信息")
@allure.story("正常获取当前关节角度")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_angles(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    with allure.step("机械臂调用 get_angles 接口获取当前角度"):
        response = device.mc.get_angles()
    with allure.step("机械臂断言返回类型为 list"):
        assert isinstance(response, list), f"机械臂响应类型错误: {type(response)}"
    with allure.step("断言角度值是否符合预期"):
        expected = eval(case["l_expect_data"])

        allure.attach(str(expected), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)

        assert_almost_equal(response,expected,tol=1,name='获取全角度'), f"机械臂角度不一致，期望: {expected}，实际: {response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

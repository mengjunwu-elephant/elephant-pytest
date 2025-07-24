import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_angles")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取角度信息")
@allure.story("正常获取当前关节角度")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_angles(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    with allure.step("左臂调用 get_angles 接口获取当前角度"):
        l_response = device.ml.get_angles()
    with allure.step("右臂调用 get_angles 接口获取当前角度"):
        r_response = device.mr.get_angles()

    with allure.step("断言返回类型为 list"):
        assert isinstance(l_response, list), f"左臂响应类型错误: {type(l_response)}"
        assert isinstance(r_response, list), f"右臂响应类型错误: {type(r_response)}"

    with allure.step("断言角度值是否符合预期"):
        expected_l = eval(case["l_expect_data"])
        expected_r = eval(case["r_expect_data"])

        allure.attach(str(expected_l), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(expected_r), name="右臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response), name="右臂实际值", attachment_type=allure.attachment_type.TEXT)

        assert l_response == expected_l, f"左臂角度不一致，期望: {expected_l}，实际: {l_response}"
        assert r_response == expected_r, f"右臂角度不一致，期望: {expected_r}，实际: {r_response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

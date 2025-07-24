import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_base_coords")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def init_coords(device):
    device.init_coords()

@allure.feature("获取基座坐标")
@allure.story("正常用例 - 获取左右臂基座坐标")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_base_coords(device, case):
    title = case['title']
    logger.info(f"》》》》》用例【{title}】开始测试《《《《《")
    logger.debug(f"test_api: {case['api']}")

    with allure.step("获取左臂基座坐标"):
        l_response = device.ml.get_base_coords()

    with allure.step("获取右臂基座坐标"):
        r_response = device.mr.get_base_coords()

    with allure.step("断言返回类型为int"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言返回结果与期望值一致"):
        # Excel中的字符串数据转成列表/元组
        expected_l = eval(case['l_expect_data'])
        expected_r = eval(case['r_expect_data'])
        assert l_response == expected_l, f"左臂期望={expected_l}，实际={l_response}"
        assert r_response == expected_r, f"右臂期望={expected_r}，实际={r_response}"

    logger.info(f"请求结果断言成功,用例【{title}】测试成功")
    logger.info(f"》》》》》用例【{title}】测试完成《《《《《")

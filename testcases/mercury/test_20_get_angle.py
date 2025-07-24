import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载 Excel 测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_angle")


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


@allure.feature("获取单个关节角度")
@allure.story("正常获取角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_angle_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    joint = case["joint"]

    with allure.step("调用 get_angle 获取左右臂角度"):
        l_response = device.ml.get_angle(joint)
        r_response = device.mr.get_angle(joint)

    with allure.step("断言类型为 float"):
        assert isinstance(l_response, float), f"左臂角度类型错误: {type(l_response)}"
        assert isinstance(r_response, float), f"右臂角度类型错误: {type(r_response)}"

    with allure.step("断言角度值是否符合预期"):
        allure.attach(str(case["l_expect_data"]), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(case["r_expect_data"]), name="右臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response), name="右臂实际值", attachment_type=allure.attachment_type.TEXT)

        assert l_response == case["l_expect_data"], f"左臂角度不一致，期望: {case['l_expect_data']}，实际: {l_response}"
        assert r_response == case["r_expect_data"], f"右臂角度不一致，期望: {case['r_expect_data']}，实际: {r_response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")


@allure.feature("获取单个关节角度")
@allure.story("异常关节索引触发异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_angle_invalid(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    joint = case["joint"]

    with allure.step("断言非法 joint 索引抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.ml.get_angle(joint)
            device.mr.get_angle(joint)

    allure.attach(str(joint), name="非法关节索引", attachment_type=allure.attachment_type.TEXT)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

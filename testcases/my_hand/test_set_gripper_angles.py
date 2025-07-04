import pytest
import allure
from time import sleep

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MyHandBase

cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_angles")

@pytest.fixture(scope="module")
def device():
    dev = MyHandBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")
@allure.feature("设置夹爪角度")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"])

def test_set_gripper_angles_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_angles:{case["angles"]}')
    logger.debug(f'test_speed:{case["speed"]}')

    with allure.step("调用 set_gripper_angles 接口"):
        set_res = device.m.set_gripper_angles(eval(case["angles"]), case["speed"])
        sleep(3)
    with allure.step("调用 get_gripper_angles 接口"):
        get_res = device.m.get_gripper_angles()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型断言失败，实际类型为{type(set_res)}"
        logger.debug('请求类型断言成功')

    with allure.step("断言设置返回值"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言获取返回值"):
        allure.attach(str(case["angles"]), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res, eval(case["angles"]),name='设置夹爪全角度')

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')
    sleep(5)

@allure.feature("设置夹爪角度")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"])
def test_set_gripper_angles_exception(device, case):
    title = case["title"]
    logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_speed:{case["speed"]}')

    with pytest.raises(ValueError, match=f".*{title}.*"):
        device.m.set_gripper_angles(eval(case["angles"]), case["speed"])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')
    sleep(5)

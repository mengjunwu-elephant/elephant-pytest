import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "set_reference_frame")


normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置基坐标系")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_set_reference_frame1(device, case):
    title = case["title"]
    expected_1 = case["expect_data_1"]
    expected_2 = case["expect_data_2"]
    coords = case["coords"]
    rftype = case["rftype"]
    bit = case["bit"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_rftype:{case["rftype"]}')


    with allure.step("设置基坐标系类型为世界"):
        set_res = device.m.set_reference_frame(rftype)
        get_res_r = device.m.get_reference_frame()

    with allure.step("调用 set_world_reference 接口"):
        get_res1 = device.m.get_coords()
        device.m.set_world_reference(eval(coords))
        time.sleep(0.1)
        get_res2 = device.m.get_coords()
        get_res_c = get_res2[bit-1] - get_res1[bit-1]
        device.m.set_world_reference([0, 0, 0, 0, 0, 0])
        logger.debug(f"set_res返回:{set_res},get_res_t返回:{get_res_r},get_res_c返回:{get_res_c}")

    with allure.step("设置基坐标系类型为默认"):
        device.m.set_reference_frame(0)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言 set_reference_frame 返回结果"):
        allure.attach(str(expected_1), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    with allure.step("断言 get_reference_frame 返回结果"):
        allure.attach(str(rftype), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res_r), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res_r == rftype, f"用例【{title}】断言失败，期望 {rftype}，实际 {get_res_r}"

    with allure.step("断言 get_coords 返回结果"):
        allure.attach(str(expected_2), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res_c), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res_c, expected_2, tol=1) #tol代表允许的误差值

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置超限基坐标系")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_set_reference_frame2(device, case):
    title = case["title"]
    rftype = case["rftype"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.set_reference_frame(rftype)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
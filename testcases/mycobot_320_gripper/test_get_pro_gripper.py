import pytest
import allure
from pymycobot.error import MyCobot320DataException

from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import Mycobot320Base

cases = get_test_data_from_excel(Mycobot320Base.GRIPPER_TEST_DATA_FILE, "get_pro_gripper")

normal_cases1 = [case for case in cases if case.get("test_type") == "normal1"]
normal_cases2 = [case for case in cases if case.get("test_type") == "normal2"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]

@pytest.fixture(scope="module")
def device():
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取Pro夹爪参数")
@allure.story("正常用例-不可设置")
@pytest.mark.parametrize("case", normal_cases1, ids=[case["title"] for case in normal_cases1])
def test_get_pro_gripper1(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters1: {case['address_get']}")

    with allure.step("调用接口获取夹爪状态"):
        response = device.m.get_pro_gripper(case['address_get'])
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "接口返回值", allure.attachment_type.TEXT)

    with allure.step("断言返回值类型"):
        if case['address_get'] == 1:
            assert isinstance(response, float), f"返回类型错误，实际为 {type(response)}"
        else:
            assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值与期望值相符"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取Pro夹爪参数")
@allure.story("正常用例-可设置")
@pytest.mark.parametrize("case", normal_cases2, ids=[case["title"] for case in normal_cases2])
def test_get_pro_gripper2(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_address_get: {case['address_get']}")
    logger.debug(f"test_address_set: {case['address_set']}")
    logger.debug(f"test_value: {case['value']}")

    with allure.step("获取修改前的值"):
        return_get = device.m.get_pro_gripper(case['address_get'])

    with allure.step("读取前, 设置夹爪参数"):
        device.m.set_pro_gripper(case['address_set'], case['value'])

    with allure.step("调用接口获取夹爪状态"):
        if case['address_set'] == 3:
            response = device.m.get_pro_gripper(case['address_get'], case['value'])
        else:
            response = device.m.get_pro_gripper(case['address_get'])
        logger.debug(f"接口返回值: {response}")
        allure.attach(str(response), "接口返回值", allure.attachment_type.TEXT)

    with allure.step("读取后, 设置夹爪参数"):
        if case['address_set'] == 3:
            device.m.set_pro_gripper(case['address_set'], return_get, case['value'])
        else:
            device.m.set_pro_gripper(case['address_set'], return_get)

    with allure.step("断言返回值类型为 int"):
            assert isinstance(response, int), f"返回类型错误，实际为 {type(response)}"

    with allure.step("断言返回值与期望值相符"):
        allure.attach(str(case['expect_data']), "期望值", allure.attachment_type.TEXT)
        allure.attach(str(response), "实际值", allure.attachment_type.TEXT)
        assert response == case['expect_data'], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取Pro夹爪参数")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_get_pro_gripper3(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_address_get: {case['address_get']}")

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.get_pro_gripper(case['address_get'])

    logger.info(f"✅ 用例【{case['title']}】测试成功")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
import unittest
from ddt import ddt, data

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyHandBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MyHandBase.TEST_DATA_FILE, "set_gripper_joint_cw")


@ddt
class TestSetGripperJointCw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = MyHandBase()  # 实例化夹爪
        logger.info("初始化完成，接口测试开始")

    @classmethod
    def tearDownClass(cls):
        cls.device.set_default_cw()  # 恢复默认状态
        cls.device.m.close()
        logger.info("环境清理完成，接口测试结束")

    @data(*[case for case in cases if case.get("test_type") == "normal"])
    def test_set_gripper_joint_cw(self, case):
        logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_joint: {case["joint"]}')
        logger.debug(f'test_parameter: {case["parameter"]}')

        set_res = self.device.m.set_gripper_joint_cw(case["joint"], case["parameter"])
        get_res = self.device.m.get_gripper_joint_cw(case["joint"])

        try:
            self.assertIsInstance(set_res, int, msg=f"返回类型错误，期望int，实际{type(set_res)}")
            self.assertEqual(set_res, case['expect_data'], "设置结果不符合预期")
            self.assertEqual(get_res, case["parameter"], "读取结果不符合预期")
        except AssertionError as e:
            logger.exception(f'请求结果断言失败: {e}')
            logger.debug(f'期望数据: {case["expect_data"]}')
            logger.debug(f'实际结果: {set_res}')
            self.fail(f"用例【{case['title']}】断言失败")
        else:
            logger.info(f'请求结果断言成功，用例【{case["title"]}】测试成功')
        finally:
            logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

    @data(*[case for case in cases if case.get("test_type") == "exception"])
    def test_out_limit(self, case):
        logger.info(f'》》》》》用例【{case["title"]}】开始测试《《《《《')
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_parameters: {case["parameter"]}')

        try:
            with self.assertRaises(ValueError, msg=f"用例{case['title']}未触发ValueError，参数为{case['parameter']}"):
                self.device.m.set_gripper_joint_cw(case["joint"], case["parameter"])
        except AssertionError:
            logger.error(f"断言失败：用例{case['title']}未触发异常")
            raise  # 重新抛出异常，让测试框架捕获
        except Exception as e:
            logger.exception(f"未预期的异常发生：{str(e)}")
            raise
        else:
            logger.info(f'请求结果断言成功，用例【{case["title"]}】测试成功')
        finally:
            logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

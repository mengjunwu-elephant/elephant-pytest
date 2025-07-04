import unittest
from ddt import ddt, data
from pymycobot.error import MercuryDataException

import settings
from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.MY_HAND_TEST_DATA_FILE, "set_hand_gripper_min_pressure")


@ddt
class TestSetHandGripperMinPressure(unittest.TestCase):


    # 初始化测试环境
    @classmethod
    def setUpClass(cls):
        cls.device = MercuryBase()  # 实例化夹爪
        logger.info("初始化完成，接口测试开始")

    # 清理测试环境
    @classmethod
    def tearDownClass(cls):
        cls.device.set_default_mini_pressure()
        cls.device.close()
        logger.info("环境清理完成，接口测试结束")

    @data(*[case for case in cases if case.get("test_type") == "normal"])  # 筛选有效等价类用例
    def test_set_hand_gripper_min_pressure(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_joint:{}'.format(case['joint']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 请求发送
        set_res = self.device.ml.set_hand_gripper_min_pressure(case["joint"], case["parameter"])
        get_res = self.device.ml.get_hand_gripper_min_pressure(case["joint"])
        try:
            # 请求结果类型断言
            if type(set_res) == int:
                logger.debug('请求类型断言成功')
            else:
                logger.debug('请求类型断言失败，实际类型为{}'.format(type(set_res)))
            # 请求结果断言
            self.assertEqual(case['expect_data'], set_res)
            self.assertEqual(get_res, case["parameter"])
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('期望数据：{}'.format(case['expect_data']))
            logger.debug('实际结果：{}'.format(set_res))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功，用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

    @data(*[case for case in cases if case.get("test_type") == "exception"])  # 筛选无效等价类用例
    def test_out_limit(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameters:{}'.format(case['parameter']))
        # 请求发送
        try:
            with self.assertRaises(MercuryDataException, msg="用例{}未触发value错误，最小启动力值为{}".format(case['title'],
                                                                                                   case['parameter'])):
                self.device.ml.set_hand_gripper_min_pressure(case["joint"], case["parameter"])
        except AssertionError:
            logger.error("断言失败：用例{}未触发异常".format(case['title']))
            raise  # 重新抛出异常，让测试框架捕获
        except Exception as e:
            logger.exception("未预期的异常发生：{}".format(str(e)))
            raise
        else:
            logger.info('请求结果断言成功，用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

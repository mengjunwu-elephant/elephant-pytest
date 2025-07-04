import unittest
from ddt import ddt, data
from time import sleep

from pymycobot.error import MercuryDataException

import settings
from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.PRO_GRIPPER_TEST_DATA_FILE, "set_pro_gripper_abs_angle")


@ddt
class TestSetProGripperAbsAngle(unittest.TestCase):


    # 初始化测试环境
    @classmethod
    def setUpClass(cls):
        cls.device = MercuryBase()  # 实例化夹爪
        logger.info("初始化完成，接口测试开始")

    # 清理测试环境
    @classmethod
    def tearDownClass(cls):
        sleep(3)
        cls.device.ml.close()
        logger.info("环境清理完成，接口测试结束")

    def tearDown(self):
        self.device.ml.set_pro_gripper_abs_angle(0)
        sleep(3)

    @data(*[case for case in cases if case.get("test_type") == 1])
    def test_set_pro_gripper_abs_angle(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_value:{}'.format(case['value']))
        # 请求发送
        response = self.device.ml.set_pro_gripper_abs_angle(case["value"])
        sleep(3)
        try:
            # 请求结果类型断言
            if type(response) == int:
                logger.debug('请求类型断言成功')
            else:
                logger.debug('请求类型断言失败，实际类型为{}'.format(type(response)))
            # 请求结果断言
            self.assertEqual(case['expect_data'], response)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('期望数据：{}'.format(case['expect_data']))
            logger.debug('实际结果：{}'.format(response))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功，用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

    @data(*[case for case in cases if case.get("test_type") == 2])
    def test_pause_and_resume(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))

        # 发送绝对角度
        abs_res = self.device.ml.set_pro_gripper_abs_angle(100)
        sleep(0.5)
        pause_res = self.device.ml.set_pro_gripper_pause()
        sleep(3)
        resume_res = self.device.ml.set_pro_gripper_resume()
        sleep(1)
        try:
            # 请求结果类型断言
            if type(abs_res and pause_res and resume_res) == int:
                logger.debug('请求类型断言成功')
            else:
                logger.debug(
                    '请求类型断言失败，实际类型为绝对角度返回{}，暂停返回{}，恢复返回{}'.format(type(abs_res), type(pause_res),
                                                                                             type(resume_res)))
            # 请求结果断言
            self.assertEqual(case['expect_data'], abs_res)
            self.assertEqual(case['expect_data'], pause_res)
            self.assertEqual(case['expect_data'], resume_res)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('期望数据：{}'.format(case['expect_data']))
            logger.debug('实际结果绝对角度返回{}，暂停返回{}，恢复返回{}'.format(abs_res, pause_res, resume_res))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功，用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

    @data(*[case for case in cases if case.get("test_type") == 3])
    def test_stop(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 发送绝对角度
        abs_res = self.device.ml.set_abs_gripper_value(100)
        sleep(0.5)
        stop_res = self.device.ml.set_pro_gripper_stop()
        try:
            # 请求结果类型断言
            if type(abs_res and stop_res) == int:
                logger.debug('请求类型断言成功')
            else:
                logger.debug(
                    '请求类型断言失败，实际类型为绝对角度返回{}，停止返回{}'.format(type(abs_res), type(stop_res)))
            # 请求结果断言
            self.assertEqual(case['expect_data'], abs_res)
            self.assertEqual(case['expect_data'], stop_res)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('期望数据：{}'.format(case['expect_data']))
            logger.debug('实际结果绝对角度返回{}，停止返回{}'.format(abs_res, stop_res))
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
        logger.debug('test_value:{}'.format(case['value']))
        # 请求发送
        try:
            with self.assertRaises(MercuryDataException,
                                   msg="用例{}未触发value错误，value值为{}".format(case['title'], case['value'])):
                self.device.ml.set_pro_gripper_abs_angle(case["value"])
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

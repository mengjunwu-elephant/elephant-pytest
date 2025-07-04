import unittest
from time import sleep

from ddt import ddt, data
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_limit_switch")


@ddt
class TestSetLimitSwitch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        水星系列初始化先左臂上电，后右臂上电
        """
        cls.device = MercuryBase()
        cls.device.ml.power_on()
        cls.device.mr.power_on()
        logger.info("初始化完成，接口测试开始")

    @classmethod
    def tearDownClass(cls):
        """
        下电顺序为先右臂下电，后左臂下电
        :return:
        """
        cls.device.mr.power_off()
        cls.device.ml.power_off()
        cls.device.close()
        logger.info("环境清理完成，接口测试结束")

    def tearDown(self):
        self.device.go_zero()

    @data(*[case for case in cases if case.get("test_type") == "normal"])
    def test_set_limit_switch(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter_1:{}'.format(case['parameter_1']))
        logger.debug('test_parameter_2:{}'.format(case['parameter_2']))
        # 左臂请求发送
        l_response = self.device.ml.set_limit_switch(case['parameter_1'], case['parameter_2'])

        # 右臂请求发送
        r_response = self.device.mr.set_limit_switch(case['parameter_1'], case['parameter_2'])
        try:
            # 请求结果类型断言
            if type(l_response) == int:
                logger.debug('左臂请求类型断言成功')
            else:
                logger.debug('左臂请求类型断言失败，实际类型为{}'.format(type(l_response)))
            if type(r_response) == int:
                logger.debug('右臂请求类型断言成功')
            else:
                logger.debug('右臂请求类型断言失败，实际类型为{}'.format(type(r_response)))
            # 请求结果断言
            self.assertEqual(case['r_expect_data'], r_response)
            self.assertEqual(case['l_expect_data'], l_response)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('左臂期望数据：{}'.format(case['l_expect_data']))
            logger.debug('右臂期望数据：{}'.format(case['r_expect_data']))
            logger.debug('左臂实际结果：{}'.format(l_response))
            logger.debug('右臂实际结果：{}'.format(r_response))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功，用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

    @data(*[case for case in cases if case.get("test_type") == "logic"])
    def test_position_feedback(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter_1:{}'.format(case['parameter_1']))
        logger.debug('test_parameter_2:{}'.format(case['parameter_2']))
        # 左臂请求发送
        l_response = self.device.ml.set_limit_switch(case['parameter_1'], case['parameter_2'])
        l_move_res = self.device.ml.send_angle(1,10,self.device.speed)
        sleep(2)
        # 右臂请求发送
        r_response = self.device.mr.set_limit_switch(case['parameter_1'], case['parameter_2'])
        r_move_res = self.device.mr.send_angle(1,10,self.device.speed)
        sleep(2)
        try:
            # 请求结果类型断言
            if type(l_response) == int:
                logger.debug('左臂请求类型断言成功')
            else:
                logger.debug('左臂请求类型断言失败，实际类型为{}'.format(type(l_move_res)))
            if type(r_response) == int:
                logger.debug('右臂请求类型断言成功')
            else:
                logger.debug('右臂请求类型断言失败，实际类型为{}'.format(type(r_move_res)))
            # 请求结果断言
            self.assertEqual(case['r_expect_data'], r_move_res)
            self.assertEqual(case['l_expect_data'], l_move_res)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('左臂期望数据：{}'.format(case['l_expect_data']))
            logger.debug('右臂期望数据：{}'.format(case['r_expect_data']))
            logger.debug('左臂实际结果：{}'.format(l_move_res))
            logger.debug('右臂实际结果：{}'.format(r_move_res))
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
        logger.debug('test_parameter_1:{}'.format(case['parameter_1']))
        logger.debug('test_parameter_2:{}'.format(case['parameter_2']))
        # 请求发送
        try:
            with self.assertRaises(MercuryDataException,
                                   msg="用例{}未触发value错误，位置超差值为{}{}".format(case['title'], case['parameter_1'],case['parameter_2'])):
                self.device.ml.set_limit_switch(case['parameter_1'], case['parameter_2'])
                self.device.mr.set_limit_switch(case['parameter_1'], case['parameter_2'])
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


    @data(*[case for case in cases if case.get("test_type") == "save_or_not"])
    def test_save_or_not(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter_1:{}'.format(case['parameter_1']))
        logger.debug('test_parameter_2:{}'.format(case['parameter_2']))
        # 左臂请求发送
        l_response = self.device.ml.set_limit_switch(case['parameter_1'], case['parameter_2'])
        # 右臂请求发送
        r_response = self.device.mr.set_limit_switch(case['parameter_1'], case['parameter_2'])

        # 设置机械臂重启
        self.device.reset()

        # 读取默认值
        l_get_res = self.device.ml.get_limit_switch()
        r_get_res = self.device.mr.get_limit_switch()
        try:
            # 请求结果断言
            self.assertEqual(eval(case['r_expect_data']), r_get_res)
            self.assertEqual(eval(case['l_expect_data']), l_get_res)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('左臂期望数据：{}'.format(case['l_expect_data']))
            logger.debug('右臂期望数据：{}'.format(case['r_expect_data']))
            logger.debug('左臂实际结果：{}'.format(l_get_res))
            logger.debug('右臂实际结果：{}'.format(r_get_res))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功，用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))
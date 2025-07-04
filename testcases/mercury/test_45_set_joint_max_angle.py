import unittest
from time import sleep

from ddt import ddt, data
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_joint_max_angle")


@ddt
class TestSetJointMaxAngle(unittest.TestCase):


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
        sleep(3)

    @data(*[case for case in cases if case.get("test_type") == "normal"])  # 筛选有效等价类用例
    @data(*cases)
    def test_set_joint_max_angle(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_id:{}'.format(case['id']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 左臂请求发送
        l_response = self.device.ml.set_joint_max_angle(case["parameter"])
        self.device.ml.send_angle(case["id"], case["parameter"], self.device.speed)  # 使机械臂运动到软件限位，判断是否能够到达
        sleep(3)
        l_get_res = self.device.is_in_position(case["parameter"], self.device.ml.get_angle(case["id"]))
        # 右臂请求发送
        r_response = self.device.mr.set_joint_max_angle(case["id"])
        self.device.mr.send_angle(case["id"], case["parameter"], self.device.speed)
        sleep(3)
        r_get_res = self.device.is_in_position(case["parameter"], self.device.mr.get_angle(case["id"]))

        # 机械臂是否到达软件限位判断
        try:
            self.assertEqual(l_get_res, 1)
            self.assertEqual(r_get_res, 1)
        except AssertionError as e:
            logger.exception("{}关节未到位软件限位，断言失败".format(case["id"]))
            logger.debug("左臂{}关节设置的软件限位值为{}，当前角度值为{}".format(case['id'], case["parameter"],
                                                                                     self.device.ml.get_angle(
                                                                                         case["id"])))
            logger.debug("右臂{}关节设置的软件限位值为{}，当前角度值为{}".format(case['id'], case["parameter"],
                                                                                     self.device.mr.get_angle(
                                                                                         case["id"])))
            self.fail("用例【{}】断言失败".format(case['title']))
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
        try:
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
            logger.info('请求结果断言成功,用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

    @data(*[case for case in cases if case.get("test_type") == "exception"])  # 筛选无效等价类用例
    def test_out_limit(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_id:{}'.format(case['id']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 请求发送
        try:
            with self.assertRaises(MercuryDataException, msg="用例{}未触发value错误，id值为{}".format(case['title'], case['id'])):
                self.device.ml.set_joint_min_angle(case["parameter"])
                self.device.mr.set_joint_min_angle(case["parameter"])
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
        logger.debug('test_id:{}'.format(case['id']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 左臂请求发送
        l_response = self.device.ml.set_joint_max_angle(case['id'],case['parameter'])
        # 右臂请求发送
        r_response = self.device.mr.set_joint_max_angle(case['id'],case['parameter'])

        # 设置机械臂重启
        self.device.reset()

        # 读取默认值
        l_get_res = self.device.ml.get_joint_max_angle(case['id'])
        r_get_res = self.device.mr.get_joint_max_angle(case['id'])
        try:
            # 请求结果类型断言
            if type(l_response) == int:
                logger.debug('左臂请求类型断言成功')
            else:
                logger.debug('左臂请求类型断言失败，实际类型为{}'.format(type(l_get_res)))
            if type(r_response) == int:
                logger.debug('右臂请求类型断言成功')
            else:
                logger.debug('右臂请求类型断言失败，实际类型为{}'.format(type(r_get_res)))
            # 请求结果断言
            self.assertEqual(case['r_expect_data'], r_get_res)
            self.assertEqual(case['l_expect_data'], l_get_res)
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
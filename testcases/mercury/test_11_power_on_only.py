import unittest

from ddt import ddt, data
from pymycobot.error import MercuryRobotException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "power_on_only")


@ddt
class TestPowerOnOnly(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        水星系列初始化先左臂上电，后右臂上电
        """
        cls.device = MercuryBase()
        logger.info("初始化完成，接口测试开始")

    @classmethod
    def tearDownClass(cls):
        """
        下电顺序为先右臂下电，后左臂下电
        :return:
        """
        cls.device.go_zero()
        cls.device.mr.power_off()
        cls.device.ml.power_off()
        cls.device.close()
        logger.info("环境清理完成，接口测试结束")

    def setUp(self):
        self.device.power_off()

    @data(*[case for case in cases if case.get("test_type") == "normal"])
    def test_power_on_only(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 左臂请求发送
        input(print("请确认末端颜色是否变黄，按回车键继续测试"))
        l_response = self.device.ml.power_on_only()

        # 右臂请求发送
        r_response = self.device.mr.power_on_only()

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


    @data(*[case for case in cases if case.get("test_type") == "emergency"])
    def test_emergency(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 左臂请求发送
        input(print("请拍下急停，按回车键继续测试"))
        l_response = self.device.ml.power_on_only()

        # 右臂请求发送
        r_response = self.device.mr.power_on_only()
        input(print("请松开急停，按回车键继续测试"))
        # 请求结果类型断言
        if l_response is None:
            logger.debug('左臂请求类型断言成功')
        else:
            logger.debug('左臂请求类型断言失败，实际类型为{}'.format(type(l_response)))
        if r_response is None:
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


    @data(*[case for case in cases if case.get("test_type") == "move"])
    def test_move(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 左臂请求发送

        self.device.ml.power_on_only()

        # 右臂请求发送
        self.device.mr.power_on_only()

        # 左右臂运动控制

        l_move_res = self.device.ml.send_angle(1,10,self.device.speed)
        r_move_res = self.device.mr.send_angle(1, 10, self.device.speed)
        _assert = input(print("请观察刚刚机械臂是否运动,如果运动输入1，不运动输入任意数字点击回车继续测试"))
        try:
            if _assert == "1":
                raise MercuryRobotException
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
        except MercuryRobotException as f:
            logger.exception('请求结果断言失败,机械臂power_on_only状态下可以运动')
            raise f
        else:
            logger.info('请求结果断言成功,用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))
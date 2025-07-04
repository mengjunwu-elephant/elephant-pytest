import unittest
from ddt import ddt, data
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot280Base

# 从Excel中提取数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "get_error_information")


@ddt
class TestGetErrorInformation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        水星系列初始化先左臂上电，后右臂上电
        """
        cls.device = Mycobot280Base()
        logger.info("初始化完成，接口测试开始")

    @classmethod
    def tearDownClass(cls):
        """
        下电顺序为先右臂下电，后左臂下电
        :return:
        """
        cls.device.mc.close()
        logger.info("环境清理完成，接口测试结束")

    def tearDown(self):
        self.device.mc.clear_error_information()
        self.device.mc.go_home()



    @data(*[case for case in cases if case.get("test_type") == "normal"])
    def test_get_error_information(self,case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 请求发送
        response = self.device.mc.get_error_information()
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
            logger.debug('期望数据：{}'.format(case['l_expect_data']))
            logger.debug('实际结果：{}'.format(response))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功,用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

    @data(*[case for case in cases if case.get("test_type") == "exception"])
    def test_singular_point_error(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 使机械臂位于奇异点，并发送坐标
        self.device.mc.send_angles([0,0,0,-20,0,0,0],self.device.speed)
        self.device.mc.send_coord(3, 300, self.device.speed)
        input(print("请观察机械臂末端是否变蓝，点击回车继续测试"))
        # 请求发送
        response = self.device.mc.get_error_information()
        try:
            # 请求结果类型断言
            if type(response) == int:
                logger.debug('请求类型断言成功')
            else:
                logger.debug('请求类型断言失败，实际类型为{}'.format(type(response)))
            # 请求结果断言
            self.assertEqual(case['r_expect_data'], response)
        except AssertionError as e:
            logger.exception('请求结果断言失败')
            logger.debug('期望数据：{}'.format(case['expect_data']))
            logger.debug('实际结果：{}'.format(response))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            logger.info('请求结果断言成功,用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

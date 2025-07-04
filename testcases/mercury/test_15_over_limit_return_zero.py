import unittest
from time import sleep

from ddt import ddt, data

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "over_limit_return_zero")


@ddt
class TestOverLimitReturnZero(unittest.TestCase):
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

    @data(*cases)
    def test_over_limit_return_zero(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameter:{}'.format(case['parameter']))
        # 先移动机械臂
        self.device.ml.send_angles(self.device.coords_init_angles,self.device.speed)
        self.device.ml.send_angles(self.device.coords_init_angles, self.device.speed)
        # 左臂请求发送
        l_response = self.device.ml.over_limit_return_zero()
        l_get_res = self.device.ml.get_angles()
        # 右臂请求发送
        r_response = self.device.mr.over_limit_return_zero()
        r_get_res = self.device.mr.get_angles()
        sleep(2)
        # 判断机械臂是否回到零位
        try:
            self.device.ml.is_in_position([0, 0, 0, 0, 0, 90, 0], 0) and self.device.mr.is_in_position([0, 0, 0, 0, 0, 90, 0],
                                                                                           0) == 1
        except Exception as e:
            logger.debug("左臂未回到零位，当前角度值为{}".format(l_get_res))
            logger.debug("右臂未回到零位，当前角度值为{}".format(r_get_res))
            self.fail("用例【{}】断言失败".format(case['title']))
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
            logger.info('请求结果断言成功,用例【{}】测试成功'.format(case['title']))
        finally:
            logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

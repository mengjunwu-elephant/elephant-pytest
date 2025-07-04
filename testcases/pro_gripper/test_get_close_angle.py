import unittest
from ddt import ddt, data
import settings
from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import ProGripperBase

# 从Excel中提取数据
cases = get_test_data_from_excel(ProGripperBase.TEST_DATA_FILE, "get_close_angle")


@ddt
class TestGetCloseAngle(unittest.TestCase):


    # 初始化测试环境
    @classmethod
    def setUpClass(cls):
        cls.device = ProGripperBase()  # 实例化夹爪
        logger.info("初始化完成，接口测试开始")

    # 清理测试环境
    @classmethod
    def tearDownClass(cls):
        cls.device.m.close()
        logger.info("环境清理完成，接口测试结束")

    @data(*cases)
    def test_get_close_angle(self, case):
        logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        logger.debug('test_api:{}'.format(case['api']))
        logger.debug('test_parameters:{}'.format(case['parameter']))
        # 请求发送
        response = self.device.m.get_gripper_io_close_value()
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

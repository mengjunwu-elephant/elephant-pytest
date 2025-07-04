import unittest
from ddt import ddt, data
from common1.test_data_handler import get_test_data_from_excel
from common1 import logger
from settings import TestMycobot320

# 从Excel中提取数据
cases = get_test_data_from_excel(TestMycobot320.TEST_DATA_FILE, "get_system_version")


@ddt
class TestGetSystemVersion(unittest.TestCase):
    # 实例化日志模块
    logger = logger

    @classmethod
    def setUpClass(cls):
        """
        单元测试前执行，初始化测试环境
        """
        cls.device = TestMycobot320()
        cls.logger.info("初始化完成，接口测试开始")

    @classmethod
    def tearDownClass(cls):
        """
        单元测试后执行，清理测试环境
        """
        cls.device.mc.close()
        cls.logger.info("环境清理完成，接口测试结束")

    @data(*[case for case in cases if case.get("test_type") == "normal"])
    def test_get_system_version(self, case):
        self.logger.info('》》》》》用例【{}】开始测试《《《《《'.format(case['title']))
        # 调试信息
        self.logger.debug('test_api:{}'.format(case['api']))
        self.logger.debug('test_parameters:{}'.format(case['parameters']))
        # 请求发送
        response = self.device.mc.get_system_version()

        try:
            # 请求结果类型断言
            if type(response) == float:
                self.logger.debug('请求类型断言成功')
            else:
                self.logger.debug('请求类型断言失败，实际类型为{}'.format(type(response)))
            # 请求结果断言
            self.assertEqual(case['expect_data'], response)
        except AssertionError as e:
            self.logger.exception('请求结果断言失败')
            self.logger.debug('期望数据：{}'.format(case['expect_data']))
            self.logger.debug('实际结果：{}'.format(response))
            self.fail("用例【{}】断言失败".format(case['title']))
        else:
            self.logger.info('请求结果断言成功,用例【{}】测试成功'.format(case['title']))
        finally:
            self.logger.info('》》》》》用例【{}】测试完成《《《《《'.format(case['title']))

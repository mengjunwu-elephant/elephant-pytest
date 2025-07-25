import pytest
from settings import CASES_DIR,REPORT_DIR
import datetime
import os
from common1 import logger

if __name__ == '__main__':
    # logger.info("开始执行接口自动化用例".center(50, "*"))
    # pytest.main()
    # logger.info("接口自动化用例执行完成".center(50, "*"))
    # logger.info("开始生成测试报告".center(50, "*"))
    # os.system("allure generate ./report/json_report/ -o ./report/html_report --clean")
    # logger.info("测试报告生成成功".center(50, "*"))




    # product_name = input("请输入数字选择需要测试的产品:\n"
    #                      "1: mercury\n"
    #                      "2: mercury_pro_gripper\n"
    #                      "3: mercury_my_hand\n"
    #                      "4: pro_gripper\n"
    #                      "5: my_hand\n"
    #                      "6: mycobot_280\n"
    #                      "7: mycobot_320\n"
    #                      )
    #
    # # 获取对应用例路径
    # case_path = CASES_DIR.get(product_name)
    # if not case_path:
    #     print("输入错误，请输入1-7之间的数字。")
    #     exit(1)

    # # 生成报告文件名（带时间戳）
    # now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # report_file = f"report_{product_name}_{now}.html"
    #
    # # 调用 pytest 执行测试并生成 html 报告
    # pytest.main([
    #     case_path,
    #     f"--html=reports/{report_file}",
    #     "--self-contained-html"  # 报告文件独立，不依赖外部资源
    # ])

# 执行 pytest 并生成 allure 原始结果
    pytest.main(["-s",
       "testcases/mycobot_280",
        f"--alluredir={REPORT_DIR}"
    ])
    pytest.main()

    print("\n✅ 测试执行完成，生成报告中...")

    # 生成并打开 Allure 报告
    os.system(f"allure generate {REPORT_DIR} -o allure-report --clean")
    os.system("allure open allure-report")
import os
import inspect
from pymycobot import *


def get_get_methods(cls):
    """
    获取类中所有以 'get' 开头的方法名
    """
    return [name for name, func in inspect.getmembers(cls, predicate=inspect.isfunction) if name.startswith("jog")]

def create_empty_test_files(methods, save_path):
    """
    为每个方法名创建一个空的 test_<method>.py 文件
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for method in methods:
        filename = f"test_{method}.py"
        filepath = os.path.join(save_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            pass  # 不写入内容
        print(f"✅ 创建空文件: {filepath}")

def main(output_dir):
    methods = get_get_methods(MyCobot280)
    create_empty_test_files(methods, output_dir)


if __name__ == "__main__":
    output_dir = "../testcases/mycobot_280"  # ✅ 可自定义路径
    main(output_dir)

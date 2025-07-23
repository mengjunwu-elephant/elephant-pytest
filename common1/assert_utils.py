import math
import allure


def assert_almost_equal(actual, expected, tol=5, name="值"):
    """
    通用容差断言：支持 int、float、list、tuple 比较

    :param actual: 实际值
    :param expected: 期望值
    :param tol: 容差范围（绝对值）
    :param name: 用于提示的变量名
    """
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        _assert_single_value(actual, expected, tol, name)

    elif isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        if len(actual) != len(expected):
            raise AssertionError(f"{name} 长度不一致：实际 {len(actual)}，期望 {len(expected)}")
        for i, (a, e) in enumerate(zip(actual, expected)):
            _assert_single_value(a, e, tol, f"{name}[{i}]")

    else:
        raise TypeError(f"不支持的数据类型：actual={type(actual)}, expected={type(expected)}")


def _assert_single_value(actual, expected, tol, name):
    delta = abs(actual - expected)
    allure.attach(
        f"期望：{expected}\n实际：{actual}\n容差：±{tol}\n偏差：{delta}",
        name=name,
        attachment_type=allure.attachment_type.TEXT
    )
    assert delta < tol, f"{name} 超出容差 ±{tol}：期望 {expected}，实际 {actual}，偏差 {delta}"
---
name: ultraarm-pytest-new-case
description: 按本仓库约定新增或改写 UltraArm pymycobot 的 pytest 用例（Excel 参数化、device fixture、Allure、hardware 标记）。在用户要求加用例、补接口测试、对齐 UltraArm_P1 或 Attachments 目录风格时使用。
---

# 新增 pytest 接口用例

## 前置判断
1. 用例归属：**本体** `testcases/UltraArm_P1/`（数据文件 `UltraArmP1Base.TEST_DATA_FILE`）或 **附件** `testcases/UltraArm_P1_Attachments/`（`ATTACHMENTS_TEST_DATA_FILE`）。
2. 是否需特殊 teardown：若会改变夹爪/IO/姿态，参考同目录是否**本地覆盖** `device` fixture；否则用根 `conftest.py` 默认 `device` 即可。

## 步骤
1. **Excel**：在对应 xlsx 中新增与文件名语义一致的 **Sheet**（名称与代码中 `get_test_data_from_excel(..., "sheet")` 一致）；首行列名含 `title`、`test_type`、`api`、`expect_data` 及接口参数列；`test_type` 为 `normal` 或 `exception`。
2. **测试模块**：新建 `test_*.py`，顶部加载 `cases = get_test_data_from_excel(...)`。
3. **结构**：`@allure.feature` / `@allure.story`；`@pytest.mark.parametrize` 按 `test_type` 过滤；`with allure.step` 包裹「调用 API →（如需）wait → 断言」。
4. **调用**：`device.mc.<api>(...)`；运动后 `device.wait()`。
5. **断言**：精确相等用 `assert`；角度/浮点列表用 `assert_almost_equal(actual, expected, tol=..., name=...)`，**不要**在调用后加逗号再接字符串（否则会构成元组而非断言消息）。
6. **异常**：`with pytest.raises(异常类型)`，异常类与同产品线下已有用例一致（如 `ultraArmP1DataException`）。
7. **可选标记**：模块级 `pytestmark = pytest.mark.smoke` 用于冒烟。

## 自检
- [ ] Sheet 名与 `get_test_data_from_excel` 第二个参数一致  
- [ ] 未手写 `hardware` 标记（`testcases` 下会自动添加）  
- [ ] 串口仅通过环境变量或 `settings` 解析，用例内不硬编码 COM  
- [ ] `docs/EXCEL_TEST_DATA.md` 与 `common1/test_data_handler.py` 行为一致（空列名、全空行）

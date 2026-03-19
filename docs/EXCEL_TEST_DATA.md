# Excel 测试数据约定（UltraArm_P1）

## 文件与路径

- 本体用例：[`test_data/UltraArm_P1.xlsx`](../test_data/UltraArm_P1.xlsx)，常量 `UltraArmP1Base.TEST_DATA_FILE`
- 附件用例：[`test_data/UltraArm_P1_Attachments.xlsx`](../test_data/UltraArm_P1_Attachments.xlsx)，`UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE`

## 工作表与列

- **Sheet 名**须与 `get_test_data_from_excel(path, "sheet_name")` 一致。
- 第 1 行为列名；**不允许空列名**；全空数据行会被跳过。
- 常用列：`title`、`test_type`、`api`、`expect_data` 及各 API 参数字段（与 `mycobot_450` 分支约定一致）。

可选在加载时传入 `required_columns=("title", "test_type", ...)` 做强校验，见 [`common1/test_data_handler.py`](../common1/test_data_handler.py)。

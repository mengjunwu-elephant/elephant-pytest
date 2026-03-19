# Excel 测试数据约定

## 文件与路径

- 机械臂本体用例：[`test_data/mycobot_450.xlsx`](../test_data/mycobot_450.xlsx)，路径常量 `Mycobot450Base.TEST_DATA_FILE`
- Pro 夹爪用例：[`test_data/pro_gripper.xlsx`](../test_data/pro_gripper.xlsx)，`Mycobot450Base.PRO_GRIPPER_TEST_DATA_FILE`

## 工作表（Sheet）

- **Sheet 名**须与代码中 `get_test_data_from_excel(path, "sheet_name")` 一致，建议与 API / 功能同名（如 `get_system_version`、`set_motor_enabled`）。

## 表头与行

| 规则 | 说明 |
|------|------|
| 第 1 行 | 列名，将作为字典的 key；**不允许空列名** |
| 第 2 行起 | 一条用例一行；**整行无有效内容**的行会被跳过 |
| 类型 | Excel 数字多为 `int`/`float`；若需复杂结构可约定某列为 JSON 字符串，在用例中 `json.loads` |

## 常用列（与现有用例一致）

| 列名 | 用途 |
|------|------|
| `title` | 用例标题，常用于 `ids=` 与日志 |
| `test_type` | 场景分类，如 `normal` / `normal1` / `exception` / `power_on` 等，用例内 `if c["test_type"] == ...` 过滤 |
| `api` | 接口名（文档/日志用） |
| `expect_data` | 期望返回值或主断言依据 |
| 其它 | 各 API 参数字段，与 `case["parameter"]` 等代码读取一致 |

## 代码加载

使用 [`common1/test_data_handler.py`](../common1/test_data_handler.py) 的 `get_test_data_from_excel`：

- 可选参数 `required_columns=("title", "test_type", ...)` 可在新增模块中强制校验表头，避免漏列静默失败。

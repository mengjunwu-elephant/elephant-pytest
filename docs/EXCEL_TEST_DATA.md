# Excel 测试数据约定（Mercury / A1）

## 文件

- 本体等：`test_data/mercury.xlsx` → `MercuryBase.TEST_DATA_FILE`
- 夹爪等：`test_data/mercury_pro_gripper.xlsx` → `MercuryBase.PRO_GRIPPER_TEST_DATA_FILE`
- 手：`test_data/mercury_my_hand.xlsx` → `MercuryBase.MY_HAND_TEST_DATA_FILE`

## 规则

- Sheet 名与 `get_test_data_from_excel(path, "sheet_name")` 一致；首行不允许空列名；全空行跳过。
- 可选：`get_test_data_from_excel(..., required_columns=("title", "test_type", ...))`。

## 单臂（Mercury A1）数据约定

- **`test_type` 不再使用 `right`、`exception_right`**（已从 `mercury.xlsx` 删除镜像行）；保留的 `left`、`exception_left` 等与用例代码中的筛选一致。
- 标题/说明中的「左臂、右臂、左右臂、双臂」已统一为 **「机械臂」**。
- 若需再次从双臂表合并，可先恢复备份 `test_data/mercury.xlsx.bak`，再运行：  
  `python scripts/migrate_test_data_single_arm.py`（会先写入 `.bak` 再覆盖 `mercury.xlsx`）。

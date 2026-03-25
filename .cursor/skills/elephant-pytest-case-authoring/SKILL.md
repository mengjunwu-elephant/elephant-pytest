---
name: elephant-pytest-case-authoring
description: >-
  Authors pymycobot hardware pytest cases in this repo: Excel-driven rows,
  Mycobot450Base/MercuryBase/etc., allure steps, assert_utils. Use when adding
  or refactoring tests under testcases/, editing xlsx-driven parametrize, or
  when the user mentions Excel 用例、Allure、device fixture、接口测试.
---

# elephant-pytest 用例编写

## 1. 选 Base 与客户端句柄

| 用例目录（示例） | settings 类 | 主要客户端 | Excel（`TEST_DATA_FILE`） |
|------------------|-------------|------------|-------------------------|
| `testcases/mycobot_450`、`mycobot450_pro_gripper` | `Mycobot450Base` | `device.mc`（`Pro450Client`） | `test_data/mycobot_450.xlsx` 等 |
| `testcases/mercury` 等双臂 | `MercuryBase` | `device.ml` / `device.mr`（`Mercury`） | `test_data/mercury.xlsx` |
| `testcases/mercury_e1` | `MercuryE1Base` | `device.mc` | `test_data/mercury_e1.xlsx` |
| `testcases/mycobot_280` | `Mycobot280Base` | `device.mc` | `test_data/mycobot_280.xlsx` |
| `testcases/UltraArm_P1` | `UltraArmP1Base` | `device.mc` | `test_data/UltraArm_P1.xlsx` |

夹爪/附件子目录可能使用 `PRO_GRIPPER_TEST_DATA_FILE`、`ATTACHMENTS_TEST_DATA_FILE` 等类属性，以 `settings` 中对应 `*Base` 为准。

## 2. Excel 数据接口

使用 `common1.test_data_handler.get_test_data_from_excel`：

```python
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

cases = get_test_data_from_excel(
    Mycobot450Base.TEST_DATA_FILE,
    "sheet_name",  # 与 xlsx 工作表名完全一致
    required_columns=("title", "api", "expect_data"),  # 可选，缺列则 ValueError
)
```

返回 `list[dict[str, Any]]`，首行为列名；全空行跳过。常见列名因 sheet 而异（如 `test_type`、`mode`），以现有同接口用例为准。

## 3. `device` fixture 模式

- **Pro 450 目录**（如 `testcases/mycobot_450/conftest.py`）：`device` 依赖 `mycobot_ip`，内部 `build_device("mycobot450", mycobot_ip)`，teardown `dev.mc.close()`。
- **其它产品线**：多数文件内 **module 级** `@pytest.fixture(scope="module") def device()`，自行 `MercuryBase()` / `Mycobot280Base()` 等，teardown 里 `close()` / `power_on()` / `default_settings()` 等按场景恢复。
- 需要覆盖默认行为时，在**更近**的 conftest 或本模块重新定义同名 fixture。

## 4. 推荐用例骨架

```python
import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "api_sheet")

@allure.feature("模块中文名")
@allure.story("场景中文名")
@pytest.mark.parametrize("case", cases, ids=[c["title"] for c in cases])
def test_example(device, case):
    with allure.step(f"步骤说明"):
        ...
    logger.info("用例 %s 完成", case["title"])
```

- 按 Excel 的 `test_type` 等拆成多个 `@pytest.mark.parametrize` 或列表推导过滤，与现有文件保持一致。
- 异常路径：`with pytest.raises(具体异常类):`，异常类型以 pymycobot 与邻近用例为准。

## 5. 断言与 Allure

- 浮点/列表容差：`common1.assert_utils.assert_almost_equal(actual, expected, tol=..., name="...")`（内部会 `allure.attach`）。
- 简单相等：可 `allure.attach` 期望/实际字符串或 JSON，再 `assert`。

## 6. 运动等待

- Pro 450：`device.wait()` 使用 `move_wait_timeout_sec`（环境变量 `MYCOBOT450_MOVE_TIMEOUT_SEC`）。
- Mercury：`MercuryBase.wait(timeout=30.0)` 等，双臂同时判断。
- 新代码避免手写无限 `while self.mc.is_moving()`；若维护旧 280 用例，注意其 `wait()` 实现与产品线差异。

## 7. 自检

- 新增/修改用例后：`pytest path/to/test_file.py --collect-only`
- 实机：`pytest path/to/test_file.py -m hardware`（`testcases` 下通常已自动带 `hardware`）

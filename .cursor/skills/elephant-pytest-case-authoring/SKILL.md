---
name: elephant-pytest-case-authoring
description: >-
  Authors pymycobot hardware pytest cases for this repository: Excel-driven
  parametrize, product-line Base classes, device fixture lifecycle, allure
  steps, and assert_utils tolerance assertions. Use when adding or refactoring
  tests under testcases/, editing xlsx sheets or ids, or when the user mentions
  Excel 用例、Allure、fixture、接口测试、参数化、超限报错、pytest.raises、
  logger.debug 参数、Mercury 双臂异常.
---

# elephant-pytest 用例编写（Excel 驱动）

## 触发条件
- 用户提到：Excel 用例、参数化、Allure 报告、fixture 生命周期、接口测试。
- 改动范围在：`testcases/**`、`common1/test_data_handler.py`、`settings.py` 中 `*Base.TEST_DATA_FILE`。

## 步骤 1：先确认产品线上下文
按目标目录选择 `settings` 基类与客户端句柄：

| 目录示例 | Base 类 | 客户端句柄 |
|---|---|---|
| `testcases/mycobot_450` | `Mycobot450Base` | `device.mc` |
| `testcases/mercury` | `MercuryBase` | `device.ml` / `device.mr` |
| `testcases/mercury_e1` | `MercuryE1Base` | `device.mc` |
| `testcases/mycobot_280` | `Mycobot280Base` | `device.mc` |
| `testcases/UltraArm_P1` | `UltraArmP1Base` | `device.mc` |

附件/夹爪目录优先检查 `*Base` 上是否使用 `ATTACHMENTS_TEST_DATA_FILE` 或 `PRO_GRIPPER_TEST_DATA_FILE`。

## 步骤 2：读取 Excel 数据
统一使用 `get_test_data_from_excel`，并尽量声明必需列：

```python
from typing import Any
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

cases: list[dict[str, Any]] = get_test_data_from_excel(
    Mycobot450Base.TEST_DATA_FILE,
    "sheet_name",
    required_columns=("title", "expect_data"),
)
```

## 步骤 3：构造测试骨架
最小骨架保持一致（可按目录调整 Base 与 case 过滤）：

```python
import allure
import pytest
from typing import Any

from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

cases: list[dict[str, Any]] = get_test_data_from_excel(
    Mycobot450Base.TEST_DATA_FILE, "api_sheet"
)

@allure.feature("模块")
@allure.story("场景")
@pytest.mark.parametrize("case", cases, ids=[str(c["title"]) for c in cases])
def test_example(device: Any, case: dict[str, Any]) -> None:
    with allure.step(f"执行: {case['title']}"):
        ...
```

### 同文件风格一致（parametrize、logger，必守）
新增或修改**同一测试文件**内的多条用例时，须与**该文件已有用例**对齐，避免混用多种写法：
- **`@pytest.mark.parametrize`**：与兄弟用例相同形态。UltraArm P1 等存量多为**单行**：`@pytest.mark.parametrize("case", [c for c in cases if ...], ids=lambda c: c["title"])`；不要在同文件内一条单行、另一条无故拆成多行且 `ids` 改为 `str(c["title"])`。过滤 `test_type` 时若需容错空白，用 `(c.get("test_type") or "").strip() == "xxx"`，仍保持单行或整文件统一换行策略。
- **`logger.debug`**：与 UltraArm P1 等存量一致时，用**逐项 f-string**，例如 `logger.debug(f'test_api:{case["api"]}')`、`logger.debug(f'axis:{case["axis"]}')`；**禁止**在同文件内对同类用例混用 `logger.debug("%s", case.get(...))` 与 f-string。Mercury 等已统一「整行 `用例详情: %s`」的目录可保持该目录内一致。
- **测试函数签名**：若同文件其它 `def test_*` 未写返回注解与 `case: dict[str, Any]`，新增用例也不要单独引入不同风格（除非整文件一并升级为 typing）。

## 步骤 4：fixture 生命周期
- Pro 450 产品线优先复用目录 `conftest.py` 的 `device`（通常来自 `build_device(...)`）。
- 若需要特殊 teardown（如夹爪复位/参数恢复），在更近作用域重定义同名 fixture，不要改全局 fixture 行为。

## 步骤 5：断言与等待
- 容差断言优先 `assert_utils.assert_almost_equal(...)`。
- 运动等待必须走 `device.wait()` 或对应 `*Base.wait(timeout=...)`。
- 禁止新增无限等待循环（如 `while is_moving(): pass`）。

## 步骤 6：超限 / 异常用例（`pytest.raises`，全产品线）
- Excel `test_type == "exception"` 等：统一 `with pytest.raises(具体异常类) as exc:`。异常类与目录一致，例如：
  - `UltraArm_P1`：`ultraArmP1DataException`
  - `mercury` / `mercury_my_hand`：`MercuryDataException`
  - `mercury_e1`：`MercuryE1DataException`
  - `mycobot_450`：`MyCobotPro450DataException`
  - `mycobot_280`：`MyCobot280DataException`
- **`raises` 块结束后**记录 **`exc.value`**（与 log/实机报错对齐）：

```python
with allure.step("断言抛出 ultraArmP1DataException"):
    with pytest.raises(ultraArmP1DataException) as exc:
        device.mc.some_api(...)

logger.info("✅ 异常断言通过,异常信息：%s", exc.value)
```

- `exc` 为 `ExceptionInfo`；在 `with` 块**内部**不要依赖已稳定的 `exc.value`。
- **Mercury 双臂、同一用例内连续两次** `pytest.raises`（先 `ml` 再 `mr`）时，勿复用同名 `exc` 覆盖左臂信息：使用 **`exc_l` / `exc_r`**，汇总一行 log，例如：
  `触发了预期异常: 左臂={exc_l.value!r} | 右臂={exc_r.value!r}`。
- 仓库已提供批量整理脚本（历史迁移用）：`scripts/codemod_pytest_raises_exc_logging.py`。

## 步骤 7：参数日志（`logger.debug` 查漏补缺）
- 每条用例在 `logger.info` 开始之后，对**本用例会参与 API 调用的字段**打 `logger.debug`（勿在 production 路径打印敏感信息）。
- 推荐（**以同文件存量为准**，见上文「同文件风格一致」）：
  - 逐项：`logger.debug(f'axis:{case["axis"]}')` 等形式；
- 若已从 `case` 解包到局部变量，至少 `logger.debug` 这些局部量，避免失败时 log 里看不到实际入参。

## 反模式（避免）
- 伪造未文档化 API 或异常类型。
- Excel sheet 名与参数化 ids 不一致，导致报告难追踪。
- 在单个 test 中混合多个接口流程，造成失败定位困难。
- 双臂异常用例里两次 `raises` 共用一个 `exc`，导致日志只保留最后一次捕获的异常。

## 自检清单
- `pytest path/to/test_file.py --collect-only`
- 若涉及实机行为：`pytest path/to/test_file.py -m hardware`

---
name: elephant-pytest-case-authoring
description: >-
  Authors pymycobot hardware pytest cases for this repository: Excel-driven
  parametrize, product-line Base classes, device fixture lifecycle, allure
  steps, assert_utils tolerance assertions, and prompt_continue operator
  confirmation. Use when adding or refactoring tests under testcases/, editing
  xlsx sheets or ids, or when the user mentions Excel 用例、Allure、fixture、
  接口测试、参数化、超限报错、pytest.raises、logger.debug 参数、Mercury 双臂异常、
  外设确认、prompt_continue、人工确认.
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
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_example(device: Any, case: dict[str, Any]) -> None:
    with allure.step(f"执行: {case['title']}"):
        ...
```

### 同文件风格一致（parametrize、logger，必守）
新增或修改**同一测试文件**内的多条用例时，须与**该文件已有用例**对齐，避免混用多种写法。

- **`@pytest.mark.parametrize`（单行，禁止自动换行）**
  - UltraArm P1 等存量统一为**整段装饰器一行写完**，参数顺序固定：`"case"` → 列表推导 → `ids=lambda c: c["title"]`。
  - **禁止**将 `@pytest.mark.parametrize` 自动折成多行（含 AI 生成、Black/Ruff 式换行、Prettier 式排版）；即使行较长也保持单行。
  - **禁止**在同文件内混用：一条单行、另一条多行；或把 `ids` 从 `lambda c: c["title"]` 改成 `[str(c["title"]) for c in ...]`。
  - 过滤 `test_type` 时若需容错空白，用 `(c.get("test_type") or "").strip() == "xxx"`，仍保持**单行**。

```python
# ✅ 正确（单行）
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])

# ❌ 错误（禁止自动换行 / 多行 parametrize）
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c["test_type"] == "normal"],
    ids=lambda c: c["title"],
)
```

- **`logger.debug`**：与 UltraArm P1 等存量一致时，用**逐项 f-string**，例如 `logger.debug(f'test_api:{case["api"]}')`、`logger.debug(f'axis:{case["axis"]}')`；**禁止**在同文件内对同类用例混用 `logger.debug("%s", case.get(...))` 与 f-string。Mercury 等已统一「整行 `用例详情: %s`」的目录可保持该目录内一致。
- **测试函数签名**：若同文件其它 `def test_*` 未写返回注解与 `case: dict[str, Any]`，新增用例也不要单独引入不同风格（除非整文件一并升级为 typing）。

## 步骤 4：fixture 生命周期
- Pro 450 产品线优先复用目录 `conftest.py` 的 `device`（通常来自 `build_device(...)`）。
- 目录级 `conftest.py` 的 `device` **只负责连接建立与关闭**（如 `yield` 后 `mc.close()`），**禁止**写入某一接口/外设专有的初始化或清理逻辑。
- **单一接口特有的环境初始化或清理**（如 PWM 关光、夹爪参数恢复、吸泵关闭、IO 复位）遵循**就近原则**：
  - 写在**对应用例所在的 `test_*.py`** 内，用 `scope="module"` 的 `autouse` fixture 或显式 fixture；
  - 参照 `test_21_set_pwm.py` 的 `teardown_pwm_modes`、`test_set_pump_state.py` 的模块确认 fixture；
  - **不要**放进目录 `conftest.py`、根 `conftest.py` 或 `settings.py`，避免未跑该接口时仍改动实机状态。
- 若某接口清理逻辑被多个**同主题**测试文件共用（如 PWM 五接口），可在每个相关文件内各写一份相同 fixture，**不要**未经确认抽到公共 `conftest`。
- 清理失败应 `logger.warning` 记录，避免裸 `except Exception: pass` 吞掉错误。

```python
@pytest.fixture(scope="module", autouse=True)
def teardown_pwm_modes(device):
    yield
    with allure.step("测试模块结束：关闭激光PWM与自定义PWM模式"):
        try:
            device.mc.set_pwm_laser_mode(0)
            device.mc.set_pwm_custom_mode(0)
        except Exception as e:
            logger.warning("模块收尾关闭PWM模式异常：%s", e)
```

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

## 步骤 8：外设 / 人工确认（`prompt_continue`）

### 何时使用
- 依赖**外设模块**（激光/PWM、吸泵、RGB 灯板、传送带、IO 治具、SD 卡、WiFi/蓝牙环境等），或需要测试人员**目视 / 扶臂 / 插拔**后再继续的用例。
- **禁止**在可用 `prompt_continue` 的场景下直接写裸 `input()`；统一走 `common1.operator_input`。

### 放置位置
- **模块级人工确认**：在**当前测试文件内**用 `autouse` fixture，**不要**擅自加到目录 `conftest.py` 作为全局 fixture（见 `.cursorrules` §九）。

```python
from common1.operator_input import prompt_continue


@pytest.fixture(scope="module", autouse=True)
def confirm_xxx_module_connected(device):
    prompt_continue("请确认XXX模块已连接，按回车继续")
    yield
```

- **步骤级人工确认**：在 `allure.step` 内、调用 API **之前**调用（例如掉使能前扶臂、观察灯色后再继续）：

```python
with allure.step("人工确认：观察末端指示灯"):
    prompt_continue("请观察机械臂末端是否变蓝，点击回车继续测试")
```

- 参照存量：`test_set_pump_state.py`、`test_21_set_pwm.py`、`test_17_set_joint_release.py`。

### `prompt_continue` 行为（`common1/operator_input.py`）
- **有 TTY**（终端 `-s` 实机跑）：`input(message)`，测试人员按回车继续。
- **无 TTY**：优先 tkinter **确定/取消**弹窗；取消且 `allow_skip=True` 时 `pytest.skip`。
- **无 TTY 且 GUI 不可用**：按 `ELEPHANT_OPERATOR_WAIT_SEC`（默认 3s）倒计时后自动继续，并写 Allure step。
- 环境变量：`ELEPHANT_OPERATOR_NO_GUI=1` 禁用弹窗；`ELEPHANT_OPERATOR_WAIT_SEC` 调整倒计时。
- Qt 探针平台会识别含 `prompt_continue` 的用例并提示存在人工交互。

### 与 `prompt_text` 的分工
- 仅需「继续 / 跳过」→ `prompt_continue`。
- 需测试人员**判通过或失败**（取消=失败）→ `prompt_text`（如无 TTY 时取消返回 `"0"`）。参照 `test_19_set_base_io_output.py`。

### 反模式（避免）
- 在 `conftest.py` 新增 session 级共用确认 fixture，导致未跑外设用例也弹窗或改变全局行为。
- 用裸 `input()` 代替 `prompt_continue`，导致无 TTY / Qt 环境下行为不一致。

## 反模式（避免）
- 伪造未文档化 API 或异常类型。
- Excel sheet 名与参数化 ids 不一致，导致报告难追踪。
- 在单个 test 中混合多个接口流程，造成失败定位困难。
- 双臂异常用例里两次 `raises` 共用一个 `exc`，导致日志只保留最后一次捕获的异常。

## 自检清单
- `pytest path/to/test_file.py --collect-only`
- 若涉及实机行为：`pytest path/to/test_file.py -m hardware`
- 外设 / 人工确认用例：`pytest path/to/test_file.py -s`（需 TTY 或 GUI 以便 `prompt_continue` 生效）

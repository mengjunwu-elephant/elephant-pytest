# elephant-pytest

基于 **pytest + allure + Excel（openpyxl）** 的机械臂（当前 **UltraArm_P1**）接口自动化测试，框架对齐 **mycobot_450** 分支：`pythonpath`、`hardware` 自动打标、环境变量连接参数、`wait()` 超时、`get_test_data_from_excel` 校验增强。

## 环境要求

- **操作系统**：Windows 10/11（串口环境）
- **Python**：建议 **3.10+**
- **硬件**：已连接 UltraArm_P1
- **Allure 命令行**：`allure generate/open`（可选）

## 快速开始

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

## 环境变量（串口 / 调试 / 超时）

| 变量 | 说明 |
|------|------|
| `ULTRAARM_PORT` | 串口，默认 `com4`（与 `settings.DEFAULT_ULTRAARM_PORT` 一致） |
| `ULTRAARM_BAUD` | 波特率，默认 `115200` |
| `ULTRAARM_DEBUG` | `0`/`false`/`no` 关闭 debug，默认开启（等价历史 `debug=1`） |
| `ULTRAARM_MOVE_TIMEOUT_SEC` | `wait()` 内 `get_run_status()` 轮询最大秒数，默认 `120` |

无需改代码即可切换串口，例如 PowerShell：

```powershell
$env:ULTRAARM_PORT = "COM7"
pytest -s testcases/UltraArm_P1 --collect-only
```

## 运行测试

### 交互入口（pytest + Allure）

```bash
python main.py
```

可选产品：`1` = `UltraArm_P1`，`2` = `UltraArm_P1_Attachments`。

### 直接使用 pytest

```bash
pytest -s testcases/UltraArm_P1 --alluredir=allure-results
pytest -s testcases/UltraArm_P1/test_1_get_system_version.py --alluredir=allure-results
```

### Marker（与 mycobot_450 一致）

`pytest.ini` 注册：`hardware`、`slow`、`smoke`、`regression`。`testcases` 下用例**默认自动打 `hardware`**。

- 无硬件 CI：`pytest testcases -m "not hardware"`
- 冒烟示例：`pytest testcases -m "smoke and not slow"`

## 框架说明

- **`conftest.py`**：`ultraarm_serial`（session）、`device`（module，默认仅 `mc.close()`）。模块内若需 **回零 / 夹爪复位 / IO 清理**，可**重新定义**同名 `device`（pytest 就近覆盖）。
- **`settings.py`**：`UltraArmP1Base`、`default_base_io_output()`（按 `base_io_pin_count` 复位底座 IO，缺省 12，可按硬件改）。
- **`docs/EXCEL_TEST_DATA.md`**：Excel 约定。

## 目录结构

- `main.py`：交互选择产品并跑 pytest + Allure
- `conftest.py`：全局 fixture、`hardware` 自动打标
- `settings.py`：用例目录、日志、设备参数
- `testcases/UltraArm_P1/`、`testcases/UltraArm_P1_Attachments/`
- `test_data/`：Excel
- `common1/`：日志、`test_data_handler` 等

## PYTHONPATH / 导入

根目录已配置 `pytest.ini` 的 `pythonpath = .`。若用「运行 Python 文件」直接跑脚本，请在项目根设置 `PYTHONPATH=.` 或使用 pytest 执行用例。

## Allure（Windows）

```bash
scoop install allure
# 或 choco install allure
```

## 常见问题

- **串口占用**：关闭串口助手等再跑测试。
- **无报告**：命令需带 `--alluredir=allure-results`，再 `allure generate`。

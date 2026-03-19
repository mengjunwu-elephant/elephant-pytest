# elephant-pytest

基于 **pytest + Allure + Excel（openpyxl）** 的 **pymycobot / Pro450** 机械臂 Python 库自动化测试工程。

## 环境

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 本地可编辑安装 pymycobot（与 PyPI 包二选一）

在 **pymycobot 源码根目录**执行：

```bash
pip install -e .
```

此时请**不要**再从 PyPI 安装同名包覆盖本地。若使用 `requirements.txt` 一键装依赖，可先**注释**其中的 `pymycobot~=...` 行，或在安装完其它依赖后单独 `pip install -e <pymycobot源码路径>`。

## 环境变量

| 变量 | 说明 |
|------|------|
| `MYCOBOT450_IP` 或 `Mycobot450_IP` | 控制器 IP；未设置时使用 `settings.DEFAULT_MYCOBOT450_IP` |
| `MYCOBOT450_DEBUG` | `0`/`false`/`no` 关闭 `Pro450Client(debug=...)`，默认开启（与历史行为一致） |
| `MYCOBOT450_MOVE_TIMEOUT_SEC` | `wait()` 中 `is_moving()` 轮询最大秒数，默认 `120` |

## 运行测试

**推荐**：在项目根目录用 pytest 执行（勿对单个用例文件点「运行」用纯 `python` 跑，否则常出现 `No module named 'common1'`）：

```bash
cd <本仓库根目录>
pytest testcases/mycobot_450/test_1_get_system_version.py -v
```

若必须在终端用 `python` 直接跑脚本，请先设置 **`PYTHONPATH` 为项目根目录**（PowerShell 示例）：

```powershell
$env:PYTHONPATH = (Get-Location).Path
python testcases/mycobot_450/test_1_get_system_version.py   # 仍建议用 pytest
```

本仓库已提供根目录 `.env`（`PYTHONPATH=.`) 与 `.vscode/settings.json`，在 Cursor/VS Code 中新建终端或配合 `python.envFile` 可减少该类错误。

```bash
# 全量（需真机）；生成 Allure 原始数据需已安装 allure-pytest
pytest testcases --alluredir=allure-results

# CI / 无硬件：排除 hardware（testcases 下用例在 conftest 中会自动打 hardware）
pytest testcases -m "not hardware"

# 冒烟 / 排除慢用例示例
pytest testcases -m "smoke and not slow"

# Allure 报告
allure serve allure-results
```

## 文档

- [Excel 用例表约定](docs/EXCEL_TEST_DATA.md)
- 共享 fixture：`conftest.py`（`device`、`mycobot_ip`）；模块内自定义 `device` 可覆盖默认 teardown（如夹爪复位、参数恢复）。

## pytest 标记

在 `pytest.ini` 中注册：`hardware`、`slow`、`smoke`。`testcases` 目录下用例默认附加 `hardware`。

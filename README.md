# elephant-pytest

基于 `pytest + allure` 的机械臂（当前包含 `UltraArm_P1`）接口自动化测试项目。

## 环境要求

- **操作系统**：Windows 10/11（当前仓库默认配置更偏向 Windows 串口环境）
- **Python**：建议 **3.10+**
- **硬件**：已连接的对应机械臂/控制器（例如 `UltraArm_P1`）
- **Allure 命令行工具**：用于生成与打开测试报告（`allure generate/open`）

## 快速开始

### 1) 创建虚拟环境并安装依赖

在项目根目录执行：

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

### 2) 配置串口与波特率（重要）

`UltraArm_P1` 的连接参数在 `settings.py` 的 `UltraArmP1Base` 中：

- 串口号：默认 `com4`
- 波特率：默认 `115200`

如果你的设备不是 `COM4`，请修改 `settings.py`：

- `UltraArmP1Base.__init__` 中的 `UltraArmP1('com4',115200,debug=1)`

### 3) 运行测试并生成 Allure 报告（推荐）

本仓库提供了一个交互式入口 `main.py`，会：
- 让你选择要测试的产品（目前 `1: UltraArm_P1`）
- 执行 `pytest`
- 输出 `allure-results/` 原始结果
- 生成并自动打开 `allure-report/` 报告

运行：

```bash
python main.py
```

## 使用 pytest 直接运行

你也可以不通过 `main.py`，直接运行 pytest。

### 运行某个产品的全部用例

```bash
pytest -s testcases/UltraArm_P1 --alluredir=allure-results
```

然后生成报告：

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

### 运行单个用例文件

```bash
pytest -s testcases/UltraArm_P1/test_2_get_modified_version.py --alluredir=allure-results
```

### 只跑某条用例（按用例名筛选）

```bash
pytest -s testcases/UltraArm_P1 -k "get_system_version" --alluredir=allure-results
```

### 使用 marker 筛选（可选）

`pytest.ini` 中已注册 `hw`、`smoke`、`regression`。若用例打上 `@pytest.mark.hw`，可在无硬件时跳过：`pytest -m "not hw"`。

## 测试数据说明

用例通常会从 Excel 读取测试数据，例如：
- `test_data/UltraArm_P1.xlsx`

用例代码里常见写法：
- `get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "<sheet_name>")`

如果出现“找不到 sheet / 数据为空”，请检查：
- Excel 文件路径是否存在
- Sheet 名称是否与用例中传入的一致

## 目录结构

- `main.py`：交互式运行入口（执行 pytest + 生成/打开 Allure 报告）
- `conftest.py`：全局 pytest 配置与共享 fixture（如 `device`），用例中无需重复定义
- `settings.py`：项目配置（用例目录映射、日志、Allure 结果目录、设备连接参数等；串口/波特率可由环境变量覆盖）
- `testcases/`：pytest 用例目录
  - `UltraArm_P1/`：UltraArm_P1 相关用例
  - `UltraArm_P1_Attachments/`：附件/扩展相关用例（如有）
- `test_data/`：测试数据（Excel）
- `common1/`：通用能力（日志、读取测试数据等）
- `scripts/`：一些独立脚本/实验代码（不一定作为 pytest 用例执行）
- `log/`：日志输出目录

## Allure 安装提示（Windows）

本项目依赖 `allure` 命令行可执行文件。若你执行 `python main.py` 或 `allure generate` 报错提示找不到 `allure`，请先安装 Allure：

- **使用 Scoop（推荐）**：

```bash
scoop install allure
```

- **使用 Chocolatey**：

```bash
choco install allure
```

安装后请确保在新终端中执行 `allure --version` 能正常输出版本号。

## 常见问题

### 1) 串口打不开 / 连接失败

- **确认串口号**：设备管理器里查看实际 `COMx`，并同步修改 `settings.py`
- **串口被占用**：关闭其它串口工具（例如串口调试助手/上位机软件）
- **权限问题**：以普通用户运行一般即可；若驱动/设备异常，请检查驱动安装

### 2) 运行 pytest 没生成报告

- 确认运行命令包含 `--alluredir=allure-results`
- 确认 `allure-results/` 目录里有内容后再执行 `allure generate`

### 3) 提示缺少依赖

在已激活虚拟环境的前提下重新安装：

```bash
pip install -r requirements.txt
```

## 约定

- 新增用例建议放在对应产品目录下：`testcases/<ProductName>/test_*.py`
- 用例数据尽量维护在 `test_data/` 的 Excel 中，便于非研发同学协作维护

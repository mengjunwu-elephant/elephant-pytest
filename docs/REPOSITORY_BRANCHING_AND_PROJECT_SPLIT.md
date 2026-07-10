# elephant-pytest 仓库与分支管理方案

本文档用于规范 pymycobot SDK 自动化测试工程的仓库拆分、目录管理和 Git 分支流程。

目标是：

- `elephant-pytest` 只负责 SDK 自动化测试、测试数据、测试辅助工具和测试报告入口。
- P1 Modbus 库、450 Modbus 库拆成独立 Python 项目，拥有自己的版本、测试和发布流程。
- 产品线差异通过目录、配置和 pytest 参数表达，不再通过长期产品分支表达。
- Git 分支只表达开发流程：主干、功能、修复、发布和归档。

## 1. 仓库边界

### 1.1 elephant-pytest

当前仓库继续作为自动化测试主仓库。

建议职责：

- 存放所有产品线的 pytest 用例。
- 存放测试数据，例如 Excel 用例数据。
- 存放测试公共 fixture、断言、日志和设备选择逻辑。
- 存放老化测试、诊断脚本、数据修复脚本等测试辅助工具。
- 存放测试平台、Allure/pytest 配置、测试执行文档。

不建议职责：

- 不长期维护独立可发布的 Modbus SDK 库代码。
- 不提交构建产物，例如 `build/`、`dist/`、`*.egg-info/`。
- 不提交运行日志、临时报告、调试输出。

### 1.2 p1-modbus

P1 Modbus 库应拆成独立项目。

推荐仓库名：

```text
p1-modbus
```

GitHub 仓库：

```text
https://github.com/mengjunwu-elephant/P1_Modbus.git
```

推荐包名：

```text
p1_modbus
```

适合独立的原因：

- 当前 `P1_Modbus/` 已经包含 `pyproject.toml`、源码包、单元测试、示例和 README。
- 它有独立版本号，例如当前 `0.3.0`。
- 它可以被 `elephant-pytest`、调试工具、生产工具或其他项目复用。

### 1.3 mycobot450-modbus

450 Modbus 库也应拆成独立项目。

推荐仓库名：

```text
mycobot450-modbus
```

GitHub 仓库：

```text
https://github.com/mengjunwu-elephant/MycobotPro450_Modbus.git
```

推荐包名：

```text
mycobot450_modbus
```

当前 `tools/modbus_prototypes/pro450_modbus.py` 更像原型脚本，拆分时应整理为标准 Python 包。

## 2. elephant-pytest 目标目录结构

建议将当前仓库逐步整理为：

```text
elephant-pytest/
  README.md
  pytest.ini
  requirements.txt
  arms.json
  conftest.py
  arm_registry.py
  settings.py

  common1/
    assert_utils.py
    log_handler.py
    operator_input.py
    test_data_handler.py

  testcases/
    mycobot_280/
    mycobot_320/
    mycobot_450/
    mycobot450_pro_gripper/
    mercury/
    mercury_e1/
    mercury_e1_pro_gripper/
    mercury_my_hand/
    mercury_pro_gripper/
    UltraArm_P1/
    UltraArm_P1_Attachments/

  test_data/
    mycobot_280.xlsx
    mycobot_320.xlsx
    mycobot_450.xlsx
    mercury.xlsx
    mercury_e1.xlsx
    UltraArm_P1.xlsx

  tools/
    aging/
      ultraarm_p1_aging.py
      mycobot_450_movement.py
      positioning_accuracy.py

    diagnostics/
      response_time.py
      response_time_serial.py
      socket_serial.py
      time_amplitude.py
      drag_teach.py

    excel/
      p1_patch_excel_rows.py
      p1_update_motion_limit_excel.py
      p1_update_attachments_pwm_sheets.py
      p1_rewrite_jog_increment_coord_sheet.py

    reports/
      p1_api_coverage_report.py

    migrations/
      codemod_pytest_raises_exc_logging.py
      remove_standard_device_fixture.py

  qt_platform/
  docs/
```

目录原则：

- 产品测试用例只放在 `testcases/<product>/`。
- 产品测试数据只放在 `test_data/`，文件名尽量和产品线一致。
- 测试辅助脚本放在 `tools/`，不要继续堆在 `scripts/` 根目录。
- 老化脚本先放在 `tools/aging/`，后续成熟后再逐步 pytest 化。
- 临时日志、报告、构建产物不要提交到仓库。

## 3. 产品线管理规则

产品线不再用长期分支区分，而是用以下方式区分：

- `testcases/<product>/`
- `test_data/<product>.xlsx`
- `arms.json`
- pytest marker
- pytest 命令参数
- CI matrix

`arms.json` 是产品线入口配置，建议每个产品至少维护：

```json
{
  "label": "MyCobot Pro 450",
  "connection_mode": "ip",
  "default_ip": "192.168.0.232",
  "device_profile": "pro450",
  "testcase_roots": [
    "testcases/mycobot_450",
    "testcases/mycobot450_pro_gripper"
  ]
}
```

新增产品线时，应同步完成：

1. 新增 `testcases/<product>/`。
2. 新增或更新 `test_data/<product>.xlsx`。
3. 更新 `arms.json`。
4. 在 README 或产品文档中增加运行说明。
5. 如需要，增加 CI matrix 配置。

## 4. P1 Modbus 拆分方案

### 4.1 新建独立仓库

在 Git 平台新建空仓库：

```text
p1-modbus
```

如果希望保留 `P1_Modbus/` 的历史，可以使用 subtree split：

```powershell
git switch main
git pull origin main
git subtree split --prefix=P1_Modbus -b split/p1-modbus
```

添加新远端并推送：

```powershell
git remote add p1-modbus <p1-modbus-repo-url>
git push p1-modbus split/p1-modbus:main
```

如果不需要保留历史，也可以直接复制 `P1_Modbus/` 内容到新仓库，然后作为新项目首次提交。

### 4.2 新项目建议结构

```text
p1-modbus/
  README.md
  pyproject.toml
  requirements.txt

  p1_modbus/
    __init__.py
    command_address.py
    commands.py
    crc.py
    errors.py
    events.py
    framing.py
    modbus_rtu.py
    models.py
    ultra_api.py
    ultra_api_limits.py

  tests/
    test_crc.py
    test_framing.py
    test_modbus_rtu.py
    test_ultra_api.py

  examples/
    basic_usage.py
```

拆分后应从新仓库删除：

```text
build/
dist/
*.egg-info/
test_report/
python_debug_*.log
```

这些属于生成物或运行日志，不应该进入独立库仓库。

### 4.3 elephant-pytest 中如何依赖

开发环境推荐使用本地 editable install：

```powershell
pip install -e ..\p1-modbus
```

如果使用 Git 依赖，可以在 `requirements.txt` 中写：

```text
p1-modbus @ git+https://github.com/mengjunwu-elephant/P1_Modbus.git@main
```

更推荐生产/稳定测试环境依赖 tag：

```text
p1-modbus @ git+https://github.com/mengjunwu-elephant/P1_Modbus.git@v0.3.0
```

## 5. 450 Modbus 拆分方案

### 5.1 新建独立仓库

在 Git 平台新建空仓库：

```text
mycobot450-modbus
```

当前来源文件：

```text
tools/modbus_prototypes/pro450_modbus.py
```

如果只从脚本开始整理，不建议直接把整个 `tools/` 目录拆过去。应该只导入 450 Modbus 相关代码。

### 5.2 新项目建议结构

```text
mycobot450-modbus/
  README.md
  pyproject.toml

  mycobot450_modbus/
    __init__.py
    client.py
    crc.py
    exceptions.py
    protocol.py
    models.py

  tests/
    test_crc.py
    test_protocol.py
    test_client_parse.py

  examples/
    basic_usage.py
```

`tools/modbus_prototypes/pro450_modbus.py` 拆分建议：

- `ModbusRTU` 串口收发、CRC、帧解析放入 `client.py` 或 `protocol.py`。
- CRC 单独放入 `crc.py`，方便单测。
- 命令地址、寄存器地址、功能码放入 `protocol.py`。
- 自定义异常放入 `exceptions.py`。
- 示例调用放入 `examples/basic_usage.py`。

### 5.3 pyproject.toml 模板

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "mycobot450-modbus"
version = "0.1.0"
description = "MyCobot 450 Modbus RTU client"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "pyserial>=3.5",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["mycobot450_modbus*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 5.4 elephant-pytest 中如何依赖

开发环境：

```powershell
pip install -e ..\mycobot450-modbus
```

稳定环境：

```text
mycobotpro450-modbus @ git+https://github.com/mengjunwu-elephant/MycobotPro450_Modbus.git@v0.1.0
```

## 6. 老化脚本管理

老化脚本先保留在 `elephant-pytest`，不要拆新项目。

原因：

- 老化测试依赖产品线、设备配置、测试数据和报告目录。
- 它更接近测试工程的一部分，而不是独立 SDK 库。
- 放在当前仓库便于统一使用 pytest、Allure、日志和设备 fixture。

当前已经迁移：

```text
tools/aging/ultraarm_p1_aging.py
tools/aging/ultraarm_p1_positioning_accuracy.py
tools/aging/mycobot_450_movement.py
tools/aging/progripper_coords_movement.py
```

后续成熟后可以 pytest 化：

```text
testcases/UltraArm_P1/aging/test_p1_aging_movement.py
testcases/mycobot_450/aging/test_450_aging_movement.py
```

并添加 marker：

```python
import pytest

@pytest.mark.hardware
@pytest.mark.slow
@pytest.mark.aging
def test_p1_aging_movement(device):
    ...
```

运行：

```powershell
pytest testcases/UltraArm_P1/aging -m aging
pytest testcases/mycobot_450/aging -m aging
```

## 7. 分支模型

### 7.1 elephant-pytest

```text
main
  唯一主干，包含所有产品线自动化测试。

feature/<scope>
  新增产品线、新增测试用例、新增工具功能。

fix/<scope>
  修复测试、fixture、数据、脚本问题。

release/sdk-<version>
  针对某个 pymycobot SDK 版本冻结测试基线。

hotfix/<scope>
  已发布测试基线的紧急修复。

archive/product/<name>
  老产品长期分支归档，只读保留。
```

产品分支，例如 `mycobot_280`、`mycobot_450`、`UltraArm_P1`，迁移完成后不再作为日常开发分支使用。

### 7.2 p1-modbus 和 mycobot450-modbus

两个独立库建议使用更接近 SDK 的分支模型：

```text
main
  稳定主干，所有提交应通过单元测试。

feature/<scope>
  新增命令、新增解析、新增示例。

fix/<scope>
  修复协议、CRC、解析、异常处理问题。

release/<version>
  发布前冻结分支，例如 release/0.3.1。

hotfix/<scope>
  已发布版本紧急修复。
```

发布版本使用 tag：

```text
v0.3.0
v0.3.1
v0.4.0
```

## 8. 日常开发流程

### 8.1 更新 main

每次开发前先更新主干：

```powershell
git switch main
git pull origin main
```

如果当前分支有未提交内容，先提交或 stash：

```powershell
git status
git stash push -m "wip: <说明>"
```

### 8.2 新增产品线测试

示例：新增 mycobot_320 测试。

```powershell
git switch main
git pull origin main
git switch -c feature/mycobot-320-tests
```

修改内容：

```text
testcases/mycobot_320/
test_data/mycobot_320.xlsx
arms.json
docs/
```

验证：

```powershell
pytest --collect-only testcases/mycobot_320
pytest testcases/mycobot_320 -m smoke
```

提交：

```powershell
git add testcases/mycobot_320 test_data/mycobot_320.xlsx arms.json docs
git commit -m "add mycobot_320 tests"
git push origin feature/mycobot-320-tests
```

通过 PR 合并回 `main`。

### 8.3 修改已有产品线测试

示例：修改 450 用例。

```powershell
git switch main
git pull origin main
git switch -c fix/mycobot-450-io-tests
```

建议只修改：

```text
testcases/mycobot_450/
test_data/mycobot_450.xlsx
```

如果修改公共 fixture，需要额外验证受影响产品：

```powershell
pytest --collect-only testcases
pytest --collect-only testcases/mycobot_280
pytest --collect-only testcases/mycobot_450
pytest --collect-only testcases/mercury_e1
```

### 8.4 修改公共工具或 fixture

公共目录包括：

```text
conftest.py
common1/
arm_registry.py
settings.py
pytest.ini
```

修改公共能力时，至少执行：

```powershell
pytest --collect-only testcases
```

如果连接真实硬件，再执行一轮 smoke：

```powershell
pytest testcases/mycobot_450 -m smoke
pytest testcases/UltraArm_P1 -m smoke
```

### 8.5 修改 p1-modbus

在 `p1-modbus` 仓库中：

```powershell
git switch main
git pull origin main
git switch -c feature/add-command-xxx
```

修改源码和单测：

```text
p1_modbus/
tests/
examples/
README.md
```

验证：

```powershell
pytest
```

提交并推送：

```powershell
git add p1_modbus tests examples README.md
git commit -m "add xxx command"
git push origin feature/add-command-xxx
```

合并后打 tag：

```powershell
git switch main
git pull origin main
git tag v0.3.1
git push origin v0.3.1
```

在 `elephant-pytest` 中更新依赖版本：

```text
p1-modbus @ git+https://github.com/mengjunwu-elephant/P1_Modbus.git@v0.3.1
```

### 8.6 修改 mycobot450-modbus

流程和 `p1-modbus` 一致。

在 `mycobot450-modbus` 仓库中：

```powershell
git switch main
git pull origin main
git switch -c fix/read-register-timeout
```

验证：

```powershell
pytest
```

发布：

```powershell
git tag v0.1.1
git push origin v0.1.1
```

在 `elephant-pytest` 中更新：

```text
mycobotpro450-modbus @ git+https://github.com/mengjunwu-elephant/MycobotPro450_Modbus.git@v0.1.1
```

## 9. 合并策略

### 9.1 普通开发分支

推荐通过 PR 合并到 `main`。

合并方式：

- 小功能、小修复：Squash merge，保持主干简洁。
- 大型迁移、产品分支收敛：Merge commit，保留上下文。
- 已共享远端分支：不要强制 rebase，不要重写历史。

### 9.2 产品分支迁移

老产品分支收敛进 `main` 时，建议创建集成分支：

```powershell
git switch main
git pull origin main
git switch -c integration/product-branches
```

逐个合并：

```powershell
git merge --no-ff --no-commit origin/mycobot_280
pytest --collect-only testcases/mycobot_280
git commit -m "merge mycobot_280 tests into main"
```

每次只合一个产品线，验证通过后再合下一个。

如果分支历史太乱，可以只导入目录：

```powershell
git checkout origin/mycobot_320 -- testcases/mycobot_320 test_data/mycobot_320.xlsx
pytest --collect-only testcases/mycobot_320
git commit -m "import mycobot_320 tests"
```

### 9.3 冲突处理原则

```text
testcases/<product>/
  优先保留该产品线最新用例，但要适配 main 的公共 fixture。

test_data/
  优先保留对应产品线最新数据，确认文件名和 arms.json 一致。

conftest.py / pytest.ini / requirements.txt
  必须人工合并，不直接整文件覆盖。

common1/ / arm_registry.py / settings.py
  视为公共能力，合并后至少执行 pytest --collect-only testcases。
```

## 10. 发布与版本管理

### 10.1 elephant-pytest

如果测试仓库需要对应 SDK 版本，建议用 release 分支或 tag：

```text
release/sdk-3.9.0
tag: test-suite-sdk-3.9.0
```

建议 tag 命名：

```text
test-suite-sdk-<pymycobot-version>
```

示例：

```powershell
git tag test-suite-sdk-3.9.0
git push origin test-suite-sdk-3.9.0
```

### 10.2 Modbus 独立库

独立库使用语义化版本：

```text
MAJOR.MINOR.PATCH
```

示例：

```text
v0.3.1
v0.4.0
v1.0.0
```

版本含义：

- PATCH：修 bug，不改变 API。
- MINOR：新增命令或能力，兼容旧 API。
- MAJOR：破坏性 API 变更。

## 11. 建议的迁移顺序

推荐按以下顺序执行，风险最低：

1. 在 `main` 新增本文档。
2. 将老产品分支合并或选择性导入到 `main`。
3. 创建 `p1-modbus` 独立仓库，迁移 `P1_Modbus/`。
4. 创建 `mycobot450-modbus` 独立仓库，整理 `tools/modbus_prototypes/pro450_modbus.py`。
5. 在 `elephant-pytest` 中改为依赖两个独立库。
6. 按用途继续维护 `tools/`。
7. 将老化脚本逐步 pytest 化。
8. 将历史产品分支改名归档为 `archive/product/<name>`。

## 12. 不建议做的事情

- 不建议继续用长期产品分支维护不同产品线。
- 不建议把 Modbus 独立库和 pytest 测试仓库长期混在一起。
- 不建议提交 `build/`、`dist/`、`*.egg-info/`、日志和运行报告。
- 不建议在公共 fixture 修改后只验证单个产品线。
- 不建议在多人共享的远端分支上强制 push。
- 不建议一次性合并所有产品分支，应该逐个产品线合并和验证。

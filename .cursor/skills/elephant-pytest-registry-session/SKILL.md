---
name: elephant-pytest-registry-session
description: >-
  Explains arms.json, arm_registry build_device/resolve_*, root conftest CLI
  options and hardware marker automation for elephant-pytest. Use when changing
  conftest, arms.json, pytest 选臂, ELEPHANT_ARM, --elephant-ip, or Qt 探针连接.
---

# arms 注册与 pytest 会话

## 1. 根 `conftest.py`（仓库根）

- **`pytest_addoption`**
  - `--elephant-arm`：机械臂 ID，对应 `arms.json` 的 `arms` 下 key；也可环境变量 `ELEPHANT_ARM`。
  - `--elephant-ip`：Pro 450 等网络设备 IP；解析顺序见 `arm_registry.resolve_device_ip`。
- **`pytest_collection_modifyitems`**：路径包含 `testcases` 的用例，若未已有 `hardware` 标记，则自动 `add_marker(pytest.mark.hardware)`。
- **不**在根 conftest 定义 `device`；各产品线在 `testcases/<产品>/conftest.py` 或单测文件内定义。

## 2. `arms.json` 结构要点

- `default_arm`：无 CLI/环境变量时的默认臂 ID。
- 每个臂：`device_profile`（`pro450`、`mercury`、`mercury_e1`、`mycobot280`、`ultraarm_p1`）、`testcase_roots`、`default_ip`（可选）、`connection_mode`（可选，可被 `get_connection_mode` 推断）。

`arm_registry.load_arms_config()` 校验结构；改 JSON 后跑 `pytest testcases --collect-only` 确认无导入错误。

## 3. `arm_registry` 常用 API

| 函数 | 用途 |
|------|------|
| `resolve_arm_id(cli_arm)` | CLI `--elephant-arm` > `ELEPHANT_ARM` > `default_arm` |
| `resolve_device_ip(arm_id, cli_ip)` | Pro 450：`cli_ip` > 环境变量 IP 链 > `arms` 的 `default_ip` > `settings.DEFAULT_MYCOBOT450_IP` |
| `build_device(arm_id, connection)` | `connection`：网络为 IP 字符串；串口可为端口名，空则工厂内读环境变量 |
| `get_testcase_roots(arm_id)` | Qt/菜单用的用例根路径列表 |
| `connection_env_var_for_arm(arm_id)` | 单连接时提示覆盖的环境变量名（如 `MYCOBOT450_IP`）；Mercury 双臂为 `None` |

`build_device` 的 `arm_id` 是 **arms.json 的 key**（如 `mycobot450`），不是 `device_profile` 字符串。

## 4. 已注册的 `device_profile` → 工厂

定义于 `arm_registry.py`：`pro450` → `Mycobot450Base`，`mercury` → `MercuryBase`，`mercury_e1` → `MercuryE1Base`，`mycobot280` → `Mycobot280Base`，`ultraarm_p1` → `UltraArmP1Base`。新增产品线需注册 `_PROFILE_BUILDERS` 并在 `arms.json` 中配置。

## 5. `pytest.ini` 标记

- `hardware`：实机/控制器
- `slow`：长耗时
- `smoke`：冒烟

排除实机：`pytest -m "not hardware"`（仅当用例可不连机时适用）。

## 6. 与 Qt 平台

`qt_platform/probe.py` 等通过 `build_device(arm_id, ip_or_serial)` 探针；修改连接解析时同步检查 `resolve_device_ip` 与 `get_connection_mode`。

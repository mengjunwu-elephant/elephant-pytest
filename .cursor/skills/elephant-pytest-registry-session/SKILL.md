---
name: elephant-pytest-registry-session
description: >-
  Explains and applies elephant-pytest arm session registry flow: arms.json
  schema, arm_registry resolve/build APIs, root conftest CLI options, and
  hardware marker automation. Use when changing conftest/arms.json, handling
  pytest 选臂、ELEPHANT_ARM、--elephant-ip, or Qt 探针连接逻辑.
---

# arms 注册与 pytest 会话（统一入口）

## 触发条件
- 用户提到：选臂、`ELEPHANT_ARM`、`--elephant-arm`、`--elephant-ip`、`arms.json`、Qt 探针连接。
- 改动范围在：`arm_registry.py`、根 `conftest.py`、`arms.json`、`qt_platform/probe.py`。

## 先判定改动类型
1. **会话参数解析**：优先看根 `conftest.py`（`pytest_addoption`、collection marker）。
2. **设备构建/连接解析**：优先看 `arm_registry.py`（`resolve_*`、`build_device`）。
3. **臂配置数据**：只改 `arms.json`，避免把配置硬编码进 Python。

## 根 conftest 约束
- 根 `conftest.py` 负责 pytest 会话入口，不承载产品线 `device` fixture。
- `testcases` 下用例若未显式标 `hardware`，由 collection 阶段自动补标。

## `arms.json` 关键字段
- `default_arm`：默认臂 ID。
- `arms.<arm_id>.device_profile`：工厂 profile（如 `pro450`、`mercury`）。
- `arms.<arm_id>.testcase_roots`：该臂对应测试目录。
- `default_ip` / `connection_mode`：按设备类型可选。

## `arm_registry` 常用规则
- `resolve_arm_id(cli_arm)`：`--elephant-arm` > `ELEPHANT_ARM` > `default_arm`。
- `resolve_device_ip(arm_id, cli_ip)`：`cli_ip` > 环境变量 > `arms.json.default_ip` > `settings.DEFAULT_*`。
- `build_device(arm_id, connection)`：`arm_id` 必须是 `arms.json` 的 key，不是 `device_profile` 名。
- 新产品线接入：同时补 `_PROFILE_BUILDERS` 映射 + `arms.json` 记录。

## 与 Qt 探针协同
- `qt_platform/probe.py` 通过 `build_device(...)` 建连。
- 修改 IP/串口判定时，必须同步回归 `resolve_device_ip` 与连接模式推断逻辑。

## 自检清单
- `pytest testcases --collect-only`
- 若改动会话参数：`pytest --help` 确认参数仍可见。
- 若改动 `arms.json`：至少验证一个 `--elephant-arm <id>` 的 collect 流程。

---
name: ultraarm-run-and-ci
description: 运行 elephant-pytest、生成 Allure 报告、用标记过滤硬件用例。在用户问如何执行测试、CI 跳过真机、串口环境变量或超时配置时使用。
---

# 运行与 CI

## 本地执行（与仓库一致）
- 交互选择套件：`python main.py`（内部 `pytest -s <套件目录> --alluredir=allure-results`，再 `allure generate` / `allure open`）。
- 直接 pytest 示例：`pytest testcases/UltraArm_P1 -s --alluredir=allure-results`（需已安装 `allure-pytest` 与 CLI）。

## 环境变量（`settings.py`）
| 变量 | 作用 |
|------|------|
| `ULTRAARM_PORT` | 串口名，覆盖默认 `DEFAULT_ULTRAARM_PORT` |
| `ULTRAARM_BAUD` | 波特率 |
| `ULTRAARM_MOVE_TIMEOUT_SEC` | `device.wait()` 最长等待（秒） |
| `ULTRAARM_DEBUG` | `0/false/no` 关闭 pymycobot debug |

## 标记（`pytest.ini`）
- `hardware`：`testcases` 下用例默认已打，真机/串口必需。
- CI 无硬件：`pytest -m "not hardware"`。
- 可选：`smoke`、`slow`、`regression`（按需打在模块或用例上）。

## 产物
- Allure 原始结果目录：`allure-results`（`REPORT_DIR`）；HTML 输出目录由 `allure generate` 指定（如 `allure-report`）。

# Modbus 独立项目拆分 Checklist

本文档是执行清单，配合 `docs/REPOSITORY_BRANCHING_AND_PROJECT_SPLIT.md` 使用。

## 1. P1 Modbus

目标仓库：

```text
p1-modbus
```

当前 GitHub 仓库：

```text
https://github.com/mengjunwu-elephant/P1_Modbus.git
```

目标包名：

```text
p1_modbus
```

当前来源：

```text
P1_Modbus/
```

当前状态：

- 已有 `pyproject.toml`
- 已有 `p1_modbus/` 源码包
- 已有 `tests/`
- 已有 `examples/`
- 已有 `README.md`
- 需要清理日志、构建产物、测试报告

建议拆分步骤：

```powershell
git switch main
git pull origin main
git subtree split --prefix=P1_Modbus -b split/p1-modbus
```

新建远端仓库后推送：

```powershell
git remote add p1-modbus https://github.com/mengjunwu-elephant/P1_Modbus.git
git push p1-modbus split/p1-modbus:main
```

在新仓库中删除或加入忽略：

```text
build/
dist/
*.egg-info/
test_report/
python_debug_*.log
```

验证：

```powershell
pip install -e .[dev]
pytest
```

发布 tag：

```powershell
git tag v0.3.0
git push origin v0.3.0
```

`elephant-pytest` 依赖方式：

```text
p1-modbus @ git+https://github.com/mengjunwu-elephant/P1_Modbus.git@v0.3.0
```

## 2. MyCobot 450 Modbus

目标仓库：

```text
mycobot450-modbus
```

当前 GitHub 仓库：

```text
https://github.com/mengjunwu-elephant/MycobotPro450_Modbus.git
```

目标包名：

```text
mycobot450_modbus
```

当前来源：

```text
tools/modbus_prototypes/pro450_modbus.py
```

当前状态：

- 目前是单文件原型脚本
- 需要整理为标准 Python 包
- 需要补 `pyproject.toml`
- 需要补单元测试
- 需要把示例调用和库代码分离

建议新项目结构：

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

从原型脚本拆分时：

- `crc16` 移入 `mycobot450_modbus/crc.py`
- `ModbusRTU` 的串口连接和收发移入 `mycobot450_modbus/client.py`
- 功能码、寄存器、命令编码移入 `mycobot450_modbus/protocol.py`
- 异常类型移入 `mycobot450_modbus/exceptions.py`
- 直接运行或调试逻辑移入 `examples/basic_usage.py`

验证：

```powershell
pip install -e .[dev]
pytest
```

发布初始 tag：

```powershell
git tag v0.1.0
git push origin v0.1.0
```

`elephant-pytest` 依赖方式：

```text
mycobotpro450-modbus @ git+https://github.com/mengjunwu-elephant/MycobotPro450_Modbus.git@v0.1.0
```

## 3. 拆分完成后的 elephant-pytest 清理

两个独立库都发布 tag 后，在 `elephant-pytest` 中：

1. 更新 `requirements.txt`，改为依赖两个独立库。
2. 删除或归档 `P1_Modbus/`。
3. 删除或归档 `tools/modbus_prototypes/pro450_modbus.py`。
4. 修改引用新包的测试代码。
5. 执行测试收集：

```powershell
pytest --collect-only testcases
```

6. 对涉及硬件的产品线执行 smoke 测试。

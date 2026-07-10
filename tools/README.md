# tools 目录说明

`tools/` 用于存放 elephant-pytest 仓库内部使用的测试辅助脚本。这里的脚本服务于测试工程，不作为独立 SDK 库发布。

目录约定：

```text
tools/
  aging/              # 老化、寿命、定位精度、长时间运动类脚本
  aging/data/         # 老化脚本所需的静态数据或历史样例数据
  diagnostics/        # 串口、响应时间、拖动示教、临时诊断脚本
  excel/              # Excel 测试数据修复、批量更新、迁移脚本
  reports/            # 覆盖率、API 清单、测试统计类脚本
  migrations/         # 仓库级批量迁移或 codemod 脚本
  firmware/           # 测试或升级流程需要的固件文件
  modbus_prototypes/  # 待拆分为独立项目的 Modbus 原型代码
```

新增脚本时优先放入对应子目录，不再新增到 `scripts/`。

如果某个脚本开始具备独立版本、独立测试、独立 README，并会被多个项目复用，应考虑拆成独立仓库。例如：

- `p1-modbus`
- `mycobot450-modbus`


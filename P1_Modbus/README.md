# P1_Modbus — Python 串口库（v0.3.0）

本目录位于仓库 **`elephant-pytest`** 根下的 `P1_Modbus/`。面向 UltraArm P1（从站地址 **`0x2E`**）的 **Modbus RTU** 风格串口协议：CRC16、粘包拆帧、**Pro450 风格三层架构**（ModbusRTU + CommandAddress + 业务类）。

协议细节以 **[`ultraArm P1协议文档.xlsx`](ultraArm%20P1协议文档.xlsx)** 与 **[`../docs/ultraArm_P1_zh.md`](../docs/ultraArm_P1_zh.md)** 为准。

---

## 架构（v0.3，对齐 Pro450）

```
UltraArmP1Modbus (ultra_api.py)   — docs 命名 + 物理量校验
        ↓
P1Client (commands.py)            — g* / m* 直接组帧
        ↓
ModbusRTU (modbus_rtu.py)         — read_p1 / write_p1 / request + PDU 工具 + 线程锁
        ↓
crc.py + framing.py               — CRC + 粘包
CommandAddress (command_address.py) — 地址常量
```

| 模块 | 职责 |
|------|------|
| **`modbus_rtu.py`** | 串口事务 + **PDU 组帧/解析**（``build_read_pdu``、``decode_*`` 等同模块） |
| **`command_address.py`** | 全部 G/M 地址常量（风格同 Pro450 ``CommandAddress``） |
| **`commands.py`** | ``P1Client``：每条指令直接 ``read_p1(A.M405)`` / ``write_p1(...)`` |
| **`ultra_api_limits.py`** | 用户侧物理量范围校验 |
| **`models.py`** | 结构化 payload（``ConveyorControl`` 等） |

---

## 安装

```bash
cd P1_Modbus
pip install -e ".[dev]"
```

- **运行依赖**：`pyserial`
- **开发依赖**（可选）：`pytest`

---

## 快速开始

```python
from p1_modbus import UltraArmP1Modbus

arm = UltraArmP1Modbus("COM5", baudrate=115200, timeout=0.5, debug=True)
try:
    print(arm.get_system_version())      # G6
    print(arm.get_angles_info())         # M405 → list[float] 度
    print(arm.get_coords_info())         # M406 → list[float] mm
    arm.stop()                           # M15
finally:
    arm.close()
```

**`debug=True`** 时自动向 stderr 打印 TX/RX 十六进制；**参数超限**在组帧前抛 `ValueError`，不会下发串口。

---

## Modbus 覆盖对照

### xlsx「modbus协议」页 — 已实现

`CommandAddress` 收录 G6/G7/G0/G1 系列、M5–M40、M50–M63、M70、M80–M83、M119、M401/M402/M405/M406、G8、M200、G11、**M600** 等（见 `p1_modbus/command_address.py`）。底层通过 ``P1Client`` 的 ``g*`` / ``m*`` 或 ``read_p1`` / ``write_p1`` 调用。

### 文档有、xlsx 未收录 — 已实现（地址待实机确认）

| 文档 API | G/M | 候选地址 | 说明 |
|----------|-----|----------|------|
| `set_conveyor_stop` | M39 | `0x000E` | 0 字节写 |
| `coord_inverse_solution` | M46 | `0x001E` | FC03 + 8B 坐标×100 |
| `angle_correct_solution` | M47 | `0x0032` | FC03 + 8B 角度×100 |
| `get_pwm_status` | M84 | `0x0033` | FC03 读 |

请用 [`scripts/probe_missing_modbus.py`](scripts/probe_missing_modbus.py) 或抓包验证后更新 `command_address.py` 中未验证地址：

```bash
cd P1_Modbus
python scripts/probe_missing_modbus.py COM5
# 或先 pip install -e ".[dev]" 后在任意目录 import p1_modbus
```

### 明确不实现

| 项 | 原因 |
|----|------|
| **M601 / M602** | 方案范围外 |
| 屏端 WiFi/SD/485/机器码/碰撞阈值等 | modbus 页无映射 |
| `_async` 闭环到位 | Modbus 层不支持 |

### pymycobot 有、本库 Modbus 无映射（只读/网络类）

`get_wifi_ip`、`check_sd_card`、`get_collision_threshold`、`receive_485_data` 等 — 需走其它通信方式，不在本库范围。

---

## 数据模型

| 类型 | 用途 |
|------|------|
| **`RgbColor(r, g, b)`** | M23，各分量 u16 BE |
| **`ConveyorControl(state, direction, speed, distance)`** | M38，10 字节 J/K/L/S |
| **`BaseIoOutput(pin_no, pin_status, pin_signal)`** | M60，6 字节 |
| **`DigitalIoOutput(pin_no, pin_signal)`** | M62，4 字节 |
| **`PreviewPose` / `KinematicsInput`** | M51/M46/M47 读请求尾 8B（×100 int16 BE） |
| **`GripperParams(j, k, l)`** | M24/M26 |
| **`ConveyorParams(payload)`** | M38 原始 10 字节（兼容） |

---

## `UltraArmP1Modbus` — 公开 API（文档命名）

命名对齐 **`docs/ultraArm_P1_zh.md`**；每个方法含中文 docstring 与参数范围说明。

### 读

| 方法 | 协议 | 返回 |
|------|------|------|
| `get_system_version` | G6 | `int` |
| `get_modify_version` | G7 | `int` |
| `get_system_screen_version` | M401 | `int` |
| `get_modify_screen_version` | M402 | `int` |
| `get_angles_info` | M405 | `list[float]` 度 |
| `get_coords_info` | M406 | `list[float]` mm |
| `get_error_information` | G8 | `list[int]` |
| `get_run_status` | M200 | `int` |
| `get_queue_size` | M600 | `int` |
| `get_motor_enable_status` | M22 | `list[int]` |
| `get_zero_calibration_state` | M119 | `list[int]` |
| `get_gripper_angle` | M50 | `int` 1–100 |
| `get_gripper_parameter(addr)` | M26 | `int` |
| `get_all_base_io_states` | M61 | `list[int]` |
| `get_base_io_state(pin_no)` | M61 | `int` |
| `get_all_end_io_states` | M63 | `list[int]` |
| `get_end_io_state(pin_no)` | M63 | `int` |
| `get_pwm_status` | M84 | `list[int]` 长度 4 |
| `coord_inverse_solution(coords)` | M46 | `list[float]` 关节角 |
| `angle_correct_solution(angles)` | M47 | `list[float]` 坐标 |

### 写 / 控制

| 方法 | 协议 | 说明 |
|------|------|------|
| `set_coords_max_speed(coords)` | G0 | 四坐标 + 内部最大速度 |
| `set_coords(...)` | G0/G1 | 四坐标 + speed；`max_speed` 选 G0/G1 |
| `set_coord` / `set_angles` / `set_angle` | G1 | 单轴/全关节 |
| `set_jog_angle` / `set_jog_coord` | M13/M14 | 点动 |
| `jog_increment_angle` / `jog_increment_coord` | M19/M20 | 步进 |
| `stop` | M15 | 急停 |
| `collision_unlock` | M5 | 碰撞解锁 |
| `set_joint_release` / `set_joint_enable` | M17/M18 | 放松/抱紧 |
| `set_color` | M23 | RGB 0–255 |
| `set_conveyor_control` | M38 | state/direction/speed/distance |
| `set_conveyor_stop` | M39 | 传送带停止 |
| `set_preview_mode(coords)` | M51 | 可达性；返回 0/1 |
| `set_base_io_output` / `set_digital_io_output` | M60/M62 | 结构化 IO |
| `set_pump_state` | M70 | 0/1/2 |
| `set_pwm_laser_mode` / `set_pwm_laser` | M80/M81 | 激光 |
| `set_pwm_custom_mode` / `set_pwm_custom` | M82/M83 | 自定义 PWM |
| `set_gripper_*` | M24–M29 | 夹爪 |
| `clear_error_status` | M40 | 清错 |
| `upgrade_restart` | G11 | 升级重启 |
| … | … | 其余见 `ultra_api.py` |

**返回值**：多数 `set_*` 成功返回 **`0`**；`set_preview_mode` 不可达返回 **`1`**。超时/协议错误继承 `P1Client.request()` 异常。

**范围校验**：关节角、坐标、速度 1–100、RGB/PWM/IO/传送带等 — 见 `ultra_api_limits.py`；超限 **`ValueError`**，不发送 Modbus。

---

## `P1Client` — 底层 G/M

除上述高层 API 外，`P1Client` 仍提供：

- **`read_p1(addr, tail)`** / **`write_p1(addr, data)`** — P1 读写原语
- **`g*` / `m*` / `read_*`** — 与 xlsx 一一对应的底层方法
- **新增**：`m39_conveyor_stop`、`m46_inverse_solution`、`m47_forward_solution`、`m84_read_pwm_status`
- **payload 修正**：`m38_conveyor(ConveyorControl)`、`m60_set_base_io(BaseIoOutput)`、`m25_gripper_angle(angle, speed)` 整型 1–100 等

寄存器摘要见 ``CommandAddress``（``python -c "from p1_modbus import CommandAddress; print(CommandAddress.G6)"``）。

---

## 事件帧

主动上报：`2E 10 00 30`（限位）、`2E 10 00 31`（碰撞）。`request()` 内自动跳过；亦可用 `poll_events()`。

```python
from p1_modbus import decode_limit_event, decode_collision_event
```

---

## 测试

```bash
cd P1_Modbus
pytest -q
```

含 `test_command_address`、`test_modbus_rtu`（golden PDU/payload）、`test_ultra_api_limits`。

---

## 对接前检查

- M39/M46/M47/M84 地址以 **实机探测** 为准。
- 运动 payload 字段顺序以 xlsx 为准；本库在 ``P1Client`` 各方法内按长度原样组帧。
- CRC：`append_crc` / `verify_crc` 自洽；与标准 Modbus 经典向量的 **整数表示** 可能相差字节序，以本库与 P1 实机一致为准。

示例脚本：[`examples/basic_usage.py`](examples/basic_usage.py)、[`scripts/probe_missing_modbus.py`](scripts/probe_missing_modbus.py)。

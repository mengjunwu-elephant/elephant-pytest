# P1_Modbus — Python 串口库

本目录位于仓库 **`elephant-pytest`** 根下的 `P1_Modbus/`。面向 UltraArm P1（从站地址 **`0x2E`**）的 **Modbus RTU** 风格串口协议：CRC16（多项式 `0xA001`，低字节在前）、粘包拆帧、指令封装。

协议细节以同目录 **[`ultraArm P1协议文档.xlsx`](ultraArm%20P1协议文档.xlsx)** 为准。

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

### 方式 A：高层 `UltraArmP1Modbus`（推荐）

`get_*` / `set_*` 命名；角度、坐标已按 **÷100** 转为浮点（度 / mm）；**首次收发自动开串口**；**`debug=True` 自动向 stderr 打 TX/RX**，无需 `logging.basicConfig`。

```python
from p1_modbus import UltraArmP1Modbus

arm = UltraArmP1Modbus("COM5", baudrate=115200, timeout=0.5, debug=True)
try:
    print(arm.get_system_version())       # G6 → int
    print(arm.get_angles())               # M405 → list[float] 度
    print(arm.get_coords())               # M406 → list[float] mm
    arm.set_estop()                       # M15 → 0
finally:
    arm.close()
```

或使用上下文：

```python
with UltraArmP1Modbus("COM5", baudrate=115200, timeout=0.5, debug=True) as arm:
    print(arm.get_errors())
```

### 方式 B：底层 `P1Client`（G/M 原始方法）

返回 **原始字节** 或 **协议数值**；适合自定义组帧或与文档逐字节对照。

```python
from p1_modbus import P1Client

with P1Client("COM5", baudrate=115200, timeout=0.5, debug=True) as bot:
    v = bot.read_main_fw_version()        # int（G6，u16 BE）
    raw = bot.m405_read_angles()          # bytes，自行解析
```

---

## 串口、调试与事务

| 行为 | 说明 |
|------|------|
| **自动打开** | 首次 `request()`、`poll_events()` 或访问 `serial` 属性时内部 `_ensure_open()`；也可显式 `open()`。 |
| **`debug=True`** | 为 logger `p1_modbus.serial` 设置 DEBUG，并在**尚无 handler** 时自动添加 **stderr** `StreamHandler`；打印 `TX` / `RX` 十六进制（空格分隔、大写）。传入自定义 `logger=` 且已有 handler 时不会重复挂载。 |
| **`event_hook`** | 可选回调 `Callable[[bytes], None]`；在 `request()` 等待应答时若收到限位/碰撞事件帧会先调用再丢弃。 |
| **`request(pdu, expect_fc=...)`** | 发送 **不含 CRC** 的 PDU，库自动追加 CRC；返回完整应答帧（含 CRC）。超时抛 `TimeoutError`；功能码不符抛 `ProtocolError`。 |

---

## 读/写帧格式（摘要）

**读 `0x03` 应答**：`2E 03 AH AL BC DATA... CRC` — `BC` 为数据字节数，解析见 `_parse_p1_read_payload`。

**写 `0x10` 请求**：`2E 10 AH AL BC DATA... CRC` — `BC` 为后续负载字节数。

**主动上报（事件）**：`2E 10 00 30 ...`（限位）、`2E 10 00 31 ...`（碰撞）；`request()` 内会自动跳过，也可用 `poll_events()` 轮询。

---

## 模块与导出

```python
from p1_modbus import (
    P1Client,
    UltraArmP1Modbus,
    ProtocolError,
    PreviewPose,
    RgbColor,
    GripperParams,
    ConveyorParams,
    decode_limit_event,
    decode_collision_event,
)
```

- **`ProtocolError`**：应答功能码或格式异常。
- **`PreviewPose`** / **`RgbColor`** / **`GripperParams`** / **`ConveyorParams`**：见下文「数据模型」。

---

## 数据模型

| 类型 | 用途 | 说明 |
|------|------|------|
| **`RgbColor(r, g, b)`** | M23 RGB | 三个分量；线上为各 16 位大端（与文档示例一致）。 |
| **`PreviewPose(payload: bytes)`** | M51 预览 | **恰好 8 字节**，由上位机按固件约定编码。 |
| **`GripperParams(j, k, l)`** | M24 / M26 | J、K、L 为 16 位无符号逻辑值；线上大端。 |
| **`ConveyorParams(payload: bytes)`** | M38 传送带 | **恰好 10 字节**。 |

---

## 事件解析

```python
from p1_modbus import decode_limit_event, decode_collision_event

for frame in arm.poll_events():
    if frame[2:4] == b"\x00\x30":
        a, b = decode_limit_event(frame)
    elif frame[2:4] == b"\x00\x31":
        a, b = decode_collision_event(frame)
```

返回 `(frame[4], frame[5])`，具体语义以固件为准。

---

## `P1Client` — 全部 G/M 接口

`P1Client` = `P1ClientBase` + `P1CommandsMixin`。下列方法均通过内部 `request()` 收发；**写类**方法返回 **完整应答 `bytes`（含 CRC）**；**读类**返回解析后的 **`int` / `tuple` / `bytes`**。

### 固件版本（主控 `0x00xx`）

| 方法 | 协议 | 返回值 | 说明 |
|------|------|--------|------|
| `read_main_fw_version()` | G6 | `int` | 2 字节负载大端 **u16**（如 `00 0A` → 10）。 |
| `read_main_fw_patch()` | G7 | `int` | 同上（如 `00 05` → 5）。 |

### 运动与控制（`payload` 为 **bytes**，长度须与文档一致）

| 方法 | 协议 | 参数 | 返回 |
|------|------|------|------|
| `g0_coordinate_max_speed(payload10)` | G0 | 10 字节 | `bytes` |
| `g1_coordinate_fixed_speed(payload10)` | G1 坐标规定速度 | 10 字节 | `bytes` |
| `g1_joint(payload10)` | G1 关节 | 10 字节 | `bytes` |
| `g1_single_coordinate(payload6)` | G1 单坐标 | 6 字节 | `bytes` |
| `g1_single_joint(payload6)` | G1 单关节 | 6 字节 | `bytes` |
| `g10_reboot_stm32()` | G10 重启 STM32 | — | `bytes` |
| `m5_unlock()` | M5 解锁 | — | `bytes` |
| `m13_continuous_joint(payload6)` | M13 持续关节 | 6 字节 | 高层见 ``set_jog_angle`` |
| `m14_continuous_coordinate(payload6)` | M14 持续坐标 | 6 字节 | 高层见 ``set_jog_coord`` |
| `m19_step_joint(payload6)` | M19 步进关节 | 6 字节 | 高层见 ``jog_increment_angle`` |
| `m20_step_coordinate(payload6)` | M20 步进坐标 | 6 字节 | 高层见 ``jog_increment_coord`` |
| `m15_estop()` | M15 急停 | — | `bytes` |
| `m17_relax_motors()` | M17 放松电机 | — | `bytes` |
| `m18_brake_motors()` | M18 抱紧电机 | — | `bytes` |

### 状态、灯、校准、传送带

| 方法 | 协议 | 返回值 / 参数 |
|------|------|----------------|
| `m22_read_motor_status()` | M22 | `tuple[int,...]` 五个字节状态 |
| `m23_rgb(color: RgbColor)` | M23 | `bytes` |
| `m30_zero_calibration(joint_index)` | M30 零位校准 | `int` 关节索引 |
| `m31_encoder_calibration_j1()` | M31 J1 编码器校准 | `bytes` |
| `m32_clear_zero_calibration(joint_index)` | M32 清除零位状态 | `bytes` |
| `m34_buzzer(on: bool)` | M34 蜂鸣器 | `bytes` |
| `m35_enable_end_button()` | M35 末端按钮使能 | `bytes` |
| `m36_disable_end_button()` | M36 末端按钮失能 | `bytes` |
| `m37_force_homing()` | M37 强制回零 | `bytes` |
| `m38_conveyor(params: ConveyorParams)` | M38 传送带 | `bytes` |
| `m40_clear_errors()` | M40 清除错误 | `bytes` |
| `m51_preview(pose: PreviewPose)` | M51 预览 | `bool`（可达为 True） |

### 零位与夹爪

| 方法 | 协议 | 返回值 / 参数 |
|------|------|----------------|
| `m119_read_zero_calibration_state()` | M119 | `tuple[int,int,int,int]` 四关节标志 |
| `m50_read_gripper_angle_centideg()` | M50 | `int` 原始 u16，**角度度值 ÷100** |
| `m25_gripper_angle(angle_centideg, speed_centideg)` | M25 | 两 u16 大端含义见文档 |
| `m24_set_gripper_params(p: GripperParams)` | M24 | `bytes` |
| `m26_read_gripper_params(p: GripperParams)` | M26 | `int` u16（查询依赖 J/K） |
| `m27_read_gripper_motion_state()` | M27 | `int` u16 BE |
| `m28_gripper_enable(enable: bool)` | M28 | `bytes` |
| `m29_gripper_zero_calibration()` | M29 | `bytes` |

### IO、吸泵、激光、自定义 PWM

| 方法 | 协议 | 参数 |
|------|------|------|
| `m70_pump(on_mask)` | M70 吸泵 | 低字节掩码 |
| `m60_set_base_io(payload6)` | M60 底座 IO | 6 字节 |
| `m61_read_base_io()` | M61 | 返回 **`bytes`** 负载 |
| `m62_set_tool_io(payload4)` | M62 末端输出 | 4 字节 |
| `m63_read_tool_io()` | M63 | 返回 **`bytes`** |
| `m80_laser_switch(on)` | M80 激光开关 | `bool` |
| `m81_laser_pwm(level)` | M81 激光 PWM 档位 | 0–255 |
| `m82_custom_pwm_switch(on)` | M82 | `bool` |
| `m83_custom_pwm_level(level)` | M83 | 0–255 |

### 屏端总线（地址区 **`0x01xx`**）

| 方法 | 协议 | 返回值 |
|------|------|--------|
| `read_display_fw_version()` | M401 | `int` u16 BE（如 `00 0C` → 12） |
| `read_display_fw_patch()` | M402 | `int` u16 BE |
| `m405_read_angles()` | M405 | **`bytes`**（大端 int16 序列，**×0.01°**） |
| `m406_read_coordinates()` | M406 | **`bytes`**（同上，一般 **×0.01 mm**） |
| `g8_read_errors()` | G8 读错误 | **`bytes`** |
| `m200_read_main_runtime_state()` | M200 | `int` 单字节状态 |
| `g11_request_stm32_fw_update()` | G11 升级请求 | `bytes` |
| `m600_read_motion_buffer_size()` | M600 缓冲区大小 | `int` u16 BE |

### 底层事务（`P1ClientBase`）

| 成员 | 说明 |
|------|------|
| `open()` / `close()` | 打开/关闭串口。 |
| `poll_events(max_frames=16)` | 非阻塞读取已到达的 **事件帧** 列表。 |
| `request(pdu_without_crc: bytes, *, expect_fc=None)` | 一次完整事务。 |

---

## `UltraArmP1Modbus` — 全部 `get_*` / `set_*`

继承 `P1Client`，故仍可使用所有 `m*` / `g*` / `read_*` 方法。下列为 **封装层** 约定：

- **`get_*`**：返回 **`int`**、**`list[int]`** 或 **`list[float]`**（角度/坐标）。
- **`set_*`**：成功返回 **`0`**；异常抛出同底层。

### `get_*` 一览

| 方法 | 对应底层 | 返回类型 | 说明 |
|------|----------|----------|------|
| `get_system_version()` | G6 | `int` | 主控版本 u16。 |
| `get_modify_version()` | G7 | `int` | 主控更正版本 u16。 |
| `get_system_screen_version()` | M401 | `int` | 屏幕版本 u16。 |
| `get_screen_modify_version()` | M402 | `int` | 屏幕更正版本 u16。 |
| `get_angles()` | M405 | `list[float]` | 各关节 **度**，int16 百分之一度 ÷100。 |
| `get_coords()` | M406 | `list[float]` | 坐标 **mm**（int16 ×0.01 ÷100）。 |
| `get_errors()` | G8 | `list[int]` | 错误负载按 **u8** 列表。 |
| `get_runtime_state()` | M200 | `int` | 运行状态字节。 |
| `get_buffer_size()` | M600 | `int` | 缓冲区大小 u16。 |
| `get_motor_status()` | M22 | `list[int]` | 五路状态。 |
| `get_zero_calibration_state()` | M119 | `list[int]` | 四关节零位标志。 |
| `get_gripper_angle_centideg()` | M50 | `int` | 夹爪角度原始 **×100** 整数。 |
| `get_gripper_motion_state()` | M27 | `int` | u16。 |
| `get_gripper_param(j, k)` | M26 | `int` | 内部 `GripperParams(j,k,0)`。 |
| `get_base_io()` | M61 | `list[int]` | 各字节 0–255。 |
| `get_tool_io()` | M63 | `list[int]` | 同上。 |
| `get_pose_preview_ok(pose8)` | M51 | `int` | `pose8` 为 **8 个 0–255**；可达 `1` 否则 `0`。 |

**示例**：

```python
reachable = arm.get_pose_preview_ok([0, 0, 0, 0, 0, 0, 0, 0])
deg = arm.get_gripper_angle_centideg() / 100.0   # 转为度（若需浮点度）
```

### `set_*` 一览

#### 角度 / 坐标 + 速度（`UltraArmP1Modbus` 封装）

与 `get_angles` / `get_coords` 一致：物理量按 **度或毫米** 传入，库内对 **目标值与速度** 做 **`×100`** 后压成 **大端 int16**（centi 单位）。**单关节 / 单坐标 6 字节**线格式为：**轴号 int16（1–4）+ 目标 int16（×100）+ 速度 int16（×100）**。例：关节 1 运动到 **0°**、速度 **100** → 负载 ``00 01 00 00 27 10``，整帧 ``2E 10 00 07 06 00 01 00 00 27 10`` + CRC。

**轴号（1–4）**：坐标 **1=X, 2=Y, 3=Z, 4=RX**；关节 **1–4**。``set_angle(axis, value, speed)`` / ``set_coord(axis, value, speed)`` 使用上述线格式（**不**先读 M405/M406）。``set_angle([int_axis, value], speed)`` 在首元为 ``int`` 且 1–4 时与三参数等价；若两元均为浮点等，则仍按 **两维目标值 + 速度** 的旧 6 字节组帧。

| 方法 | 协议 | 参数 | 线长 |
|------|------|------|------|
| `set_coords(x, y, z, rx, speed, *, max_speed=True)` | G0 / G1 坐标 | 五元：X,Y,Z,RX + speed；`max_speed=True` 为 G0，``False`` 为 G1 | 10 |
| `set_coords([x,y,z,rx], speed, *, max_speed=True)` | 同上 | 兼容列表 + speed | 10 |
| `set_coord(axis, value, speed)` | G1 单坐标 | 轴号 1–4 + 单维目标 + speed（6B 线格式同上） | 6 |
| `set_coord([axis, value], speed)` | G1 单坐标 | 首元须 ``int`` 且 1–4 时与三参数等价 | 6 |
| `set_coord([a,b], speed)` | G1 单坐标 | 两浮点：两坐标分量 + speed（旧式两 int16） | 6 |
| `set_angles(j1, j2, j3, j4, speed)` | G1 关节 | 四关节 + speed | 10 |
| `set_angles([j1..j4], speed)` | 同上 | 兼容列表 + speed | 10 |
| `set_angle(axis, value, speed)` | G1 单关节 | 轴号 1–4 + 角度 + speed（6B 线格式） | 6 |
| `set_angle([axis, value], speed)` | G1 单关节 | 首元须 ``int`` 且 1–4 时与三参数等价 | 6 |
| `set_angle([j_a,j_b], speed)` | G1 单关节 | 两浮点：两关节角 + speed（旧式） | 6 |

**点动 / 步进（M13/M14/M19/M20）6 字节**（大端 int16×3）：**字节 1–2** 轴号 **1–4**（关节 A–D 或坐标 X,Y,Z,RX）；**字节 3–4** 对点动为方向 **D**（**1** 正向，**0** 反向），对步进为步进角/步进位移（**×100**，与角度/坐标物理量一致）；**字节 5–6** 速度 **F**（**×100**，与 ``set_angle`` 速度相同编码）。

| 方法 | 协议 | 参数 | 线长 |
|------|------|------|------|
| `set_jog_angle(joint, direction, speed)` | M13 | 关节 1–4、``direction`` 1/0 或 ``True``/``False``、速度 | 6 |
| `set_jog_coord(axis, direction, speed)` | M14 | 坐标轴 1–4、方向、速度 | 6 |
| `jog_increment_angle(joint, step_angle, speed)` | M19 | 关节 1–4、步进角度（度）、速度 | 6 |
| `jog_increment_coord(axis, step, speed)` | M20 | 轴 1–4、步进位移、速度 | 6 |

```python
# G0 最大速度坐标（推荐：按轴 1–4 = X,Y,Z,RX）
arm.set_coords(10.0, 20.0, 30.0, 40.0, 50.0)
arm.set_coords([10.0, 20.0, 30.0, 40.0], 50.0)  # 与上等价
# G1 规定速度坐标
arm.set_coords(10.0, 20.0, 30.0, 40.0, 50.0, max_speed=False)
# 单关节：关节 1 → 0°，速度 100（线负载 00 01 00 00 27 10）
print(arm.set_angle(1, 0, 100))
# 只改 Z（轴 3），单坐标线格式同上
arm.set_coord(3, 100.0, 25.0)
arm.set_angles(0.0, 10.0, -5.0, 3.0, 30.0)
print(arm.set_angle(1, 10.0, 100.0))   # 关节 1 → 10°，速度 100
# 关节 2 正向点动，速度 80
arm.set_jog_angle(2, True, 80.0)
# Z 轴反向点动，速度 50
arm.set_jog_coord(3, 0, 50.0)
# 关节 1 步进 0.5°，速度 100
arm.jog_increment_angle(1, 0.5, 100.0)
arm.jog_increment_coord(1, 1.0, 60.0)  # X 步进 1mm（若设备为 mm）
```

底层若需 **原始 10/6 字节**，仍请使用 `P1Client.g0_coordinate_max_speed(bytes)` 等自行组帧。

#### 其它 `set_*`

| 方法 | 协议 | 参数 | 返回 |
|------|------|------|------|
| `set_reboot_stm32()` | G10 | — | `0` |
| `set_unlock()` | M5 | — | `0` |
| `set_estop()` | M15 | — | `0` |
| `set_relax_motors()` | M17 | — | `0` |
| `set_brake_motors()` | M18 | — | `0` |
| `set_rgb(r, g, b)` | M23 | 三个 `int` | `0` |
| `set_zero_calibration(joint_index)` | M30 | 关节索引 | `0` |
| `set_encoder_calibration_j1()` | M31 | — | `0` |
| `set_clear_zero_calibration(joint_index)` | M32 | 关节索引 | `0` |
| `set_buzzer(on)` | M34 | `bool` | `0` |
| `set_end_button_enable()` | M35 | — | `0` |
| `set_end_button_disable()` | M36 | — | `0` |
| `set_force_homing()` | M37 | — | `0` |
| `set_conveyor(payload10)` | M38 | `Sequence[int]` 长度 **10**（原始字节低 8 位） | `0` |
| `set_clear_errors()` | M40 | — | `0` |
| `set_gripper_angle(angle_centideg, speed_centideg)` | M25 | 两 `int` | `0` |
| `set_gripper_params(j, k, l_val)` | M24 | 三 16 位参数 | `0` |
| `set_gripper_enable(enable)` | M28 | `bool` | `0` |
| `set_gripper_zero_calibration()` | M29 | — | `0` |
| `set_pump(on_mask)` | M70 | 0–255 掩码 | `0` |
| `set_base_io(payload6)` | M60 | 长度 6 | `0` |
| `set_tool_io(payload4)` | M62 | 长度 4 | `0` |
| `set_laser_switch(on)` | M80 | `bool` | `0` |
| `set_laser_pwm(level)` | M81 | 0–255 | `0` |
| `set_custom_pwm_switch(on)` | M82 | `bool` | `0` |
| `set_custom_pwm_level(level)` | M83 | 0–255 | `0` |
| `set_stm32_fw_update_request()` | G11 | — | `0` |

**`payloadN`（非运动类）**：`list` / `tuple` 中每个元素取 **低 8 位** 作为一字节，长度须等于 **N**。

---

## 其它子模块（扩展/测试）

| 模块 | 作用 |
|------|------|
| `p1_modbus.crc` | `crc16_modbus`、`append_crc`、`verify_crc` |
| `p1_modbus.framing` | `pop_first_frame`、`SLAVE_ID` |
| `p1_modbus.errors` | `ProtocolError` |

---

## 测试

```bash
cd P1_Modbus
pytest -q
```

---

## 对接前检查

- 版本、角度、坐标的解析以 **实机回读** 与 **xlsx** 一致为准；若与抓包不符，优先核对 `BC` 与寄存器布局。
- 运动类 **10/6 字节 payload** 的字段顺序、单位以厂家文档为准，本库只负责按长度原样下发。

更多脚本示例见 [`examples/basic_usage.py`](examples/basic_usage.py)、仓库 [`../demo/P1_modbus_demo.py`](../demo/P1_modbus_demo.py)。

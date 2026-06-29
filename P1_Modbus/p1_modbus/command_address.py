"""P1 Modbus 指令地址常量（对齐 xlsx modbus协议页 + 文档补全项，不含 M601/M602）."""


class CommandAddress:
    """指令地址常量类（风格对齐 Pro450 ``CommandAddress``）。"""

    # --- 主控 0x00xx ---
    G6 = 0x0001
    G7 = 0x0002
    G0 = 0x0003
    G1_COORD = 0x0004
    G1_JOINT = 0x0005
    G1_SINGLE_COORD = 0x0006
    G1_SINGLE_JOINT = 0x0007
    G10 = 0x0008
    M5 = 0x0009
    M13 = 0x000A
    M14 = 0x000B
    M19 = 0x000C
    M20 = 0x000D
    M39 = 0x000E  # xlsx 未收录，待实机确认
    M15 = 0x000F
    M17 = 0x0010
    M18 = 0x0011
    M22 = 0x0012
    M23 = 0x0013
    M30 = 0x0014
    M31 = 0x0015
    M32 = 0x0016
    M34 = 0x0017
    M35 = 0x0018
    M36 = 0x0019
    M37 = 0x001A
    M38 = 0x001B
    M40 = 0x001C
    M51 = 0x001D
    M46 = 0x0033  # 坐标逆解（FC03 + 8B 坐标×100）
    M119 = 0x001F
    M50 = 0x0020
    M25 = 0x0021
    M24 = 0x0022
    M26 = 0x0023
    M27 = 0x0024
    M28 = 0x0025
    M29 = 0x0026
    M70 = 0x0027
    M60 = 0x0028
    M61 = 0x0029
    M62 = 0x002A
    M63 = 0x002B
    M80 = 0x002C
    M81 = 0x002D
    M82 = 0x002E
    M83 = 0x002F
    M84 = 0x0032  # PWM 状态读（4 字节）
    M47 = 0x0034  # 角度正解（FC03 + 8B 角度×100）

    # --- 屏端 0x01xx ---
    M401 = 0x0101
    M402 = 0x0102
    M405 = 0x0104
    M406 = 0x0105
    G8 = 0x0106
    M200 = 0x0107
    G11 = 0x0108
    M600 = 0x0109


# 主动上报事件子地址（非 G/M 读写表项）
EVENT_LIMIT = 0x0030
EVENT_COLLISION = 0x0031

UNVERIFIED_ADDRS: frozenset[int] = frozenset(
    {
        CommandAddress.M39,
        CommandAddress.M46,
        CommandAddress.M47,
        CommandAddress.M84,
    }
)
